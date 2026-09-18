"""CME Futures Instruments Model."""

# pylint: disable=unused-argument

import asyncio
from datetime import (
    date as dateType,
    datetime,
)
from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.futures_instruments import (
    FuturesInstrumentsData,
    FuturesInstrumentsQueryParams,
)
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import ConfigDict, Field, field_validator

from openbb_cme.utils.catalog import resolve_product
from openbb_cme.utils.client import CMEHttpClient
from openbb_cme.utils.helpers import fetch_product_calendar


class CMEFuturesInstrumentsQueryParams(FuturesInstrumentsQueryParams):
    """
    CME Futures Instruments Query — lists available contracts and expiration dates.

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


class CMEFuturesInstrumentData(FuturesInstrumentsData):
    """CME Futures Instrument — listed contract with expiration details."""

    model_config = ConfigDict(extra="ignore")
    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    root_symbol: str = Field(description="CME root (product) symbol (e.g. 'ES', 'NQ').")
    name: str = Field(description="Full product name.")
    exchange: str = Field(description="Exchange (e.g. 'CME/Globex').")
    expiration_date: datetime | None = Field(
        default=None, description="Contract expiration date and time (exchange local)."
    )
    description: str | None = Field(
        default=None, description="Human-readable contract description."
    )
    contract_month: str | None = Field(
        default=None, description="Exchange-published contract month."
    )
    first_trade_date: dateType | None = Field(
        default=None, description="First trading date."
    )
    last_trade_date: dateType | None = Field(
        default=None, description="Last trading date."
    )
    settlement_date: dateType | None = Field(
        default=None, description="Final settlement date."
    )
    is_active: bool = Field(
        default=True,
        description="Whether this contract is currently listed for trading.",
    )


class CMEFuturesInstrumentsFetcher(
    Fetcher[CMEFuturesInstrumentsQueryParams, list[CMEFuturesInstrumentData]]
):
    """CME Futures Instruments Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> CMEFuturesInstrumentsQueryParams:
        """Transform the query."""
        return CMEFuturesInstrumentsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: CMEFuturesInstrumentsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Fetch listed contracts from CME product calendar."""
        symbols = query.symbol.split(",")

        async def fetch_one(symbol: str, client: CMEHttpClient) -> list[dict]:
            product = await resolve_product(symbol, "Futures", client=client)
            if not product:
                raise ValueError(
                    f"Symbol '{symbol}' was not found in the CME futures catalog."
                )
            rows = await fetch_product_calendar(
                product["product_id"], "Futures", client
            )
            enriched: list[dict] = []
            for row in rows:

                def parse_date(value: str | None) -> dateType | None:
                    if not value or value == "-":
                        return None
                    try:
                        return datetime.strptime(value, "%d %b %Y").date()
                    except ValueError:
                        return None

                enriched.append(
                    {
                        "symbol": row.get("symbol", ""),
                        "root_symbol": symbol,
                        "name": product["name"],
                        "exchange": product["exchange"],
                        "expiration_date": row.get("expiration"),
                        "description": (
                            f"{product['name']} {row.get('contract_month', '')}".strip()
                        ),
                        "contract_month": row.get("contract_month"),
                        "first_trade_date": parse_date(row.get("first_trade_date")),
                        "last_trade_date": parse_date(row.get("last_trade_date")),
                        "settlement_date": parse_date(row.get("settlement_date")),
                        "is_active": row.get("is_active", True),
                    }
                )
            return enriched

        async with CMEHttpClient() as client:
            nested = await asyncio.gather(*(fetch_one(s, client) for s in symbols))
            rows = [row for result in nested for row in result]

        if not rows:
            raise EmptyDataError("No instrument data found for the given symbols.")

        return sorted(
            rows, key=lambda x: (x["root_symbol"], x.get("expiration_date") or "")
        )

    @staticmethod
    def transform_data(
        query: CMEFuturesInstrumentsQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[CMEFuturesInstrumentData]:
        """Transform the data."""
        return [CMEFuturesInstrumentData.model_validate(d) for d in data]
