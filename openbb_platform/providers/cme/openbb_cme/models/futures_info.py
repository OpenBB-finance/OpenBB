"""CME Futures Info Model."""

# pylint: disable=unused-argument

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

from openbb_cme.utils.helpers import (
    CME_PRODUCT_MAP,
    fetch_latest_settlements,
)


class CMEFuturesInfoQueryParams(FuturesInfoQueryParams):
    """
    CME Futures Info Query — contract specifications and latest settlement.

    Source: https://www.cmegroup.com/CmeWS/mvc/Settlements/Futures/Settlements/{product_id}/FUT
    """

    __json_schema_extra__ = {
        "symbol": {
            "multiple_items_allowed": True,
            "choices": list(CME_PRODUCT_MAP),
        },
    }

    symbol: str = Field(
        default="ES",
        description=QUERY_DESCRIPTIONS.get("symbol", "")
        + " One or more CME root symbols separated by commas."
        + " Supported: "
        + ", ".join(CME_PRODUCT_MAP),
    )

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def _validate_symbol(cls, v: str) -> str:
        """Validate all requested symbols."""
        symbols = [s.strip().upper() for s in v.split(",")]
        unsupported = [s for s in symbols if s not in CME_PRODUCT_MAP]
        if unsupported:
            raise ValueError(
                f"Unsupported symbols: {', '.join(unsupported)}."
                f" Supported: {', '.join(CME_PRODUCT_MAP)}"
            )
        return ",".join(symbols)


class CMEFuturesInfoData(FuturesInfoData):
    """CME Futures Contract Specifications and Latest Settlement."""

    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    name: str = Field(description="Full contract name.")
    exchange: str = Field(description="Exchange where the contract trades.")
    tick_size: float = Field(
        description="Minimum price fluctuation (tick size).",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    point_value: float = Field(
        description="Dollar value of one full index point.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    multiplier: float = Field(description="Contract multiplier (same as point_value).")
    currency: str = Field(description="Settlement currency.")
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
        # pylint: disable=import-outside-toplevel
        import asyncio

        symbols = query.symbol.split(",")

        async def fetch_one(symbol: str) -> dict | None:
            spec = CME_PRODUCT_MAP.get(symbol)
            if not spec:
                return None
            trade_date, rows = await fetch_latest_settlements(symbol)
            # Front month = lowest expiration with a settlement price
            front = next(
                (r for r in rows if r.get("settlement_price") is not None), None
            )
            return {
                "symbol": symbol,
                "name": spec["name"],
                "exchange": spec["exchange"],
                "tick_size": spec["tick_size"],
                "point_value": spec["point_value"],
                "multiplier": spec["multiplier"],
                "currency": spec["currency"],
                "settlement_price": front.get("settlement_price") if front else None,
                "open_interest": front.get("open_interest") if front else None,
                "volume": front.get("volume") if front else None,
                "front_month": front.get("expiration") if front else None,
                "trade_date": trade_date,
            }

        results_raw = await asyncio.gather(
            *[fetch_one(s) for s in symbols], return_exceptions=True
        )

        for r in results_raw:
            if isinstance(r, Exception):
                # pylint: disable=import-outside-toplevel
                from openbb_core.app.model.abstract.error import OpenBBError

                if isinstance(r, OpenBBError):
                    raise r

        results = [r for r in results_raw if isinstance(r, dict)]

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
