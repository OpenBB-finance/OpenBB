"""CME Futures Info Model."""

# pylint: disable=unused-argument

import asyncio
import re
from datetime import date as dateType
from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.futures_info import (
    FuturesInfoData,
    FuturesInfoQueryParams,
)
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field, field_validator

from openbb_cme.utils.catalog import (
    fetch_contract_specifications,
    resolve_product,
)
from openbb_cme.utils.client import CMEHttpClient
from openbb_cme.utils.helpers import (
    fetch_latest_settlements,
)


def _first_number(value: Any) -> float | None:
    """Parse the first decimal number from a contract-specification value."""
    match = re.search(r"-?\d+(?:,\d{3})*(?:\.\d+)?", str(value or ""))
    return float(match.group().replace(",", "")) if match else None


def _parse_tick_size(value: Any) -> float | None:
    """Parse decimal and fractional minimum-tick descriptions."""
    text = str(value or "")
    fractions = re.findall(r"(\d+)\s*/\s*(\d+)", text)
    if fractions:
        ratios = [
            int(numerator) / int(denominator) for numerator, denominator in fractions
        ]
        if " of " in text.lower() and len(ratios) > 1:
            return ratios[0] * ratios[1]
        if "cent" in text.lower() or "point" in text.lower():
            return ratios[0]
    return _first_number(text)


class CMEFuturesInfoQueryParams(FuturesInfoQueryParams):
    """
    CME Futures Info Query — contract specifications and latest settlement.

    Source: https://www.cmegroup.com/CmeWS/mvc/Settlements/Futures/Settlements/{product_id}/FUT
    """

    __json_schema_extra__ = {"symbol": {"multiple_items_allowed": True}}

    symbol: str = Field(
        default="ES",
        description=QUERY_DESCRIPTIONS.get("symbol", "")
        + " One or more CME root symbols separated by commas."
        + " Symbols are resolved from the live CME product slate.",
    )

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def _validate_symbol(cls, v: str) -> str:
        """Normalize all requested symbols."""
        symbols = [s.strip().upper() for s in str(v).split(",") if s.strip()]
        if not symbols:
            raise ValueError("At least one symbol is required.")
        return ",".join(symbols)


class CMEFuturesInfoData(FuturesInfoData):
    """CME Futures Contract Specifications and Latest Settlement."""

    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    name: str = Field(description="Full contract name.")
    exchange: str = Field(description="Exchange where the contract trades.")
    product_id: int = Field(description="CME website product identifier.")
    asset_class: str = Field(description="CME product group or asset class.")
    tick_size: float | None = Field(
        default=None,
        description="Minimum price fluctuation (tick size).",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    point_value: float | None = Field(
        default=None,
        description="Dollar value of one full index point.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    multiplier: float | None = Field(
        default=None, description="Contract multiplier when it can be parsed."
    )
    currency: str | None = Field(default=None, description="Settlement currency.")
    contract_unit: str | None = Field(
        default=None, description="Exchange-published contract unit."
    )
    price_quotation: str | None = Field(
        default=None, description="Exchange-published price quotation."
    )
    minimum_price_fluctuation: dict | str | None = Field(
        default=None, description="Complete exchange-published tick rules."
    )
    listed_contracts: dict | str | None = Field(
        default=None, description="Exchange-published listing cycle."
    )
    trading_hours: dict | str | None = Field(
        default=None, description="Trading hours by venue."
    )
    settlement_method: str | None = Field(
        default=None, description="Settlement method."
    )
    termination_of_trading: dict | str | None = Field(
        default=None, description="Termination-of-trading rules."
    )
    specification_url: str | None = Field(
        default=None, description="Official CME contract-specification URL."
    )
    settlement_price: float | None = Field(
        default=None,
        description="Most recent official CME settlement price.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    open_interest: float | None = Field(
        default=None, description="Most recent open interest (outstanding contracts)."
    )
    volume: float | None = Field(
        default=None,
        description="Most recent daily trading volume.",
        json_schema_extra={"x-unit_measurement": "shares"},
    )
    front_month: str | None = Field(
        default=None,
        description="Active front-month contract expiration in YYYY-MM format.",
    )
    trade_date: dateType | None = Field(
        default=None, description="Trade date of the settlement data."
    )


class CMEFuturesInfoFetcher(
    Fetcher[CMEFuturesInfoQueryParams, list[CMEFuturesInfoData]]
):
    """CME Futures Info Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> CMEFuturesInfoQueryParams:
        """Transform the query."""
        return CMEFuturesInfoQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: CMEFuturesInfoQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Fetch specs + latest settlement for each requested symbol."""
        symbols = query.symbol.split(",")

        async def fetch_one(symbol: str, client: CMEHttpClient) -> dict:
            product = await resolve_product(symbol, "Futures", client=client)
            if not product:
                raise ValueError(
                    f"Symbol '{symbol}' was not found in the CME futures catalog."
                )
            (trade_date, rows), specs = await asyncio.gather(
                fetch_latest_settlements(
                    symbol,
                    product_id=product["product_id"],
                    client=client,
                ),
                fetch_contract_specifications(product["product_id"], client),
            )
            # Front month = lowest expiration with a settlement price
            front = next(
                (r for r in rows if r.get("settlement_price") is not None), None
            )

            minimum_tick = specs.get("MinimumPriceFluctuation")
            tick_text: Any = minimum_tick
            if isinstance(minimum_tick, dict):
                ticks = minimum_tick.get("ticks", [])
                tick_text = ticks[0].get("mintk") if ticks else None
            contract_unit = specs.get("ContractUnit")
            multiplier = _first_number(contract_unit)

            return {
                "symbol": symbol,
                "name": product["name"],
                "exchange": product["exchange"],
                "product_id": product["product_id"],
                "asset_class": product["asset_class"],
                "tick_size": _parse_tick_size(tick_text),
                "point_value": multiplier,
                "multiplier": multiplier,
                "currency": "USD" if "$" in str(contract_unit) else None,
                "contract_unit": contract_unit,
                "price_quotation": specs.get("PriceQuotation"),
                "minimum_price_fluctuation": minimum_tick,
                "listed_contracts": specs.get("ListedContracts"),
                "trading_hours": specs.get("TradingHours"),
                "settlement_method": specs.get("SettlementMethod"),
                "termination_of_trading": specs.get("TerminationOfTrading"),
                "specification_url": product.get("specification_url"),
                "settlement_price": front.get("settlement_price") if front else None,
                "open_interest": front.get("open_interest") if front else None,
                "volume": front.get("volume") if front else None,
                "front_month": front.get("expiration") if front else None,
                "trade_date": trade_date,
            }

        async with CMEHttpClient() as client:
            results = await asyncio.gather(*(fetch_one(s, client) for s in symbols))

        if not results:
            raise EmptyDataError("No data found for the given symbols.")

        return results

    @staticmethod
    def transform_data(
        query: CMEFuturesInfoQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[CMEFuturesInfoData]:
        """Transform the data."""
        return [CMEFuturesInfoData.model_validate(d) for d in data]
