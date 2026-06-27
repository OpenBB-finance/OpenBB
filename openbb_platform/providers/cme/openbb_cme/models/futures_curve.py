"""CME Futures Curve Model."""

# pylint: disable=unused-argument

from datetime import date as dateType
from typing import Any

from openbb_cme.utils.helpers import (
    CME_PRODUCT_MAP,
    fetch_settlements,
    last_business_day,
)
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.futures_curve import (
    FuturesCurveData,
    FuturesCurveQueryParams,
)
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field, field_validator


class CMEFuturesCurveQueryParams(FuturesCurveQueryParams):
    """
    CME Futures Curve Query.

    Source: https://www.cmegroup.com/CmeWS/mvc/Settlements/Futures/Settlements/{product_id}/FUT
    """

    __json_schema_extra__ = {
        "symbol": {"multiple_items_allowed": False, "choices": list(CME_PRODUCT_MAP)}
    }

    symbol: str = Field(
        default="ES",
        description=QUERY_DESCRIPTIONS.get("symbol", "")
        + " Supported symbols: "
        + ", ".join(CME_PRODUCT_MAP),
    )

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def _validate_symbol(cls, v: str) -> str:
        """Uppercase and validate against known CME symbols."""
        v = v.upper()
        if v not in CME_PRODUCT_MAP:
            raise ValueError(
                f"Symbol '{v}' is not supported. Supported: {', '.join(CME_PRODUCT_MAP)}"
            )
        return v


class CMEFuturesCurveData(FuturesCurveData):
    """CME Futures Curve Data."""

    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    open_interest: float | None = Field(
        default=None, description="Open interest for this contract month."
    )
    volume: float | None = Field(
        default=None, description=DATA_DESCRIPTIONS.get("volume", "")
    )


class CMEFuturesCurveFetcher(
    Fetcher[CMEFuturesCurveQueryParams, list[CMEFuturesCurveData]]
):
    """CME Futures Curve Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> CMEFuturesCurveQueryParams:
        """Transform the query."""
        return CMEFuturesCurveQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: CMEFuturesCurveQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Fetch the term structure for the given symbol on a specific date."""
        if query.date:
            trade_date = (
                dateType.fromisoformat(query.date)
                if isinstance(query.date, str)
                else query.date
            )
        else:
            trade_date = last_business_day()

        rows = await fetch_settlements(query.symbol, trade_date)

        if not rows:
            raise EmptyDataError(
                f"No settlement data found for {query.symbol} on {trade_date}."
            )
        return rows

    @staticmethod
    def transform_data(
        query: CMEFuturesCurveQueryParams, data: list[dict], **kwargs: Any
    ) -> list[CMEFuturesCurveData]:
        """Transform the data into the FuturesCurveData model."""
        results: list[CMEFuturesCurveData] = []
        for row in data:
            price = row.get("close") or row.get("settlement_price")
            if price is None:
                continue
            results.append(
                CMEFuturesCurveData.model_validate(
                    {
                        "date": row.get("date"),
                        "expiration": row.get("expiration"),
                        "price": price,
                        "symbol": row.get("symbol"),
                        "open_interest": row.get("open_interest"),
                        "volume": row.get("volume"),
                    }
                )
            )
        if not results:
            raise EmptyDataError("No settlement prices found in the response.")
        return sorted(results, key=lambda x: x.expiration)
