"""CME Futures Curve Model."""

# pylint: disable=unused-argument

import asyncio
from datetime import date as dateType
from typing import Any

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

from openbb_cme.utils.catalog import resolve_product
from openbb_cme.utils.client import CMEHttpClient
from openbb_cme.utils.helpers import (
    fetch_latest_settlements,
    fetch_settlements,
)


class CMEFuturesCurveQueryParams(FuturesCurveQueryParams):
    """
    CME Futures Curve Query.

    Source: https://www.cmegroup.com/CmeWS/mvc/Settlements/Futures/Settlements/{product_id}/FUT
    """

    __json_schema_extra__ = {"symbol": {"multiple_items_allowed": False}}

    symbol: str = Field(
        default="ES",
        description=QUERY_DESCRIPTIONS.get("symbol", "")
        + " Enter any futures product code from the CME product slate.",
    )

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def _validate_symbol(cls, v: str) -> str:
        """Normalize a CME product code."""
        value = str(v).strip().upper()
        if not value:
            raise ValueError("Symbol cannot be empty.")
        return value


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
        async with CMEHttpClient() as client:
            product = await resolve_product(query.symbol, "Futures", client=client)
            if not product:
                raise ValueError(
                    f"Symbol '{query.symbol}' was not found in the CME futures catalog."
                )

            if query.date:
                dates = (
                    [
                        dateType.fromisoformat(value.strip())
                        for value in query.date.split(",")
                        if value.strip()
                    ]
                    if isinstance(query.date, str)
                    else [query.date]
                )
                rows_nested = await asyncio.gather(
                    *[
                        fetch_settlements(
                            query.symbol,
                            trade_date,
                            product["product_id"],
                            client,
                        )
                        for trade_date in dates
                    ]
                )
                rows = [row for result in rows_nested for row in result]
            else:
                _, rows = await fetch_latest_settlements(
                    query.symbol,
                    product_id=product["product_id"],
                    client=client,
                )

        if not rows:
            raise EmptyDataError(
                f"No settlement data found for {query.symbol} on the requested date(s)."
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
        return sorted(results, key=lambda x: (x.date or dateType.min, x.expiration))
