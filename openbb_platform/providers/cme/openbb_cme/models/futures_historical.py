"""CME Futures Historical Model."""

# pylint: disable=unused-argument

import asyncio
from datetime import (
    date as dateType,
    timedelta,
)
from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.futures_historical import (
    FuturesHistoricalData,
    FuturesHistoricalQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field, field_validator, model_validator

from openbb_cme.utils.catalog import resolve_product
from openbb_cme.utils.client import CMEHttpClient
from openbb_cme.utils.helpers import (
    business_days_between,
    fetch_settlements,
)

MAX_HISTORY_DAYS = 252
_REQUEST_SEMAPHORE_LIMIT = 10


class CMEFuturesHistoricalQueryParams(FuturesHistoricalQueryParams):
    """
    CME Futures Historical Price Query.

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

    @model_validator(mode="before")
    @classmethod
    def _apply_defaults(cls, values: dict) -> dict:
        """Default start/end if not supplied."""
        if not values.get("end_date"):
            values["end_date"] = dateType.today().strftime("%Y-%m-%d")
        if not values.get("start_date"):
            start = dateType.today() - timedelta(days=30)
            values["start_date"] = start.strftime("%Y-%m-%d")
        return values


class CMEFuturesHistoricalData(FuturesHistoricalData):
    """CME Futures Historical Data."""

    symbol: str = Field(description="The CME root symbol (e.g. 'ES', 'NQ').")
    expiration: str = Field(description="Contract expiration month in YYYY-MM format.")
    settlement_price: float | None = Field(
        default=None,
        description="Official CME daily settlement price.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    open_interest: float | None = Field(
        default=None,
        description="Daily open interest (number of outstanding contracts).",
    )


class CMEFuturesHistoricalFetcher(
    Fetcher[CMEFuturesHistoricalQueryParams, list[CMEFuturesHistoricalData]]
):
    """CME Futures Historical Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> CMEFuturesHistoricalQueryParams:
        """Transform the query."""
        return CMEFuturesHistoricalQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: CMEFuturesHistoricalQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Fetch settlement data for each business day in the requested range."""
        async with CMEHttpClient() as client:
            product = await resolve_product(query.symbol, "Futures", client=client)
            if not product:
                raise ValueError(
                    f"Symbol '{query.symbol}' was not found in the CME futures catalog."
                )

            start = query.start_date or (dateType.today() - timedelta(days=30))
            end = query.end_date or dateType.today()

            if isinstance(start, str):
                start = dateType.fromisoformat(start)
            if isinstance(end, str):
                end = dateType.fromisoformat(end)

            days = business_days_between(start, end)

            if len(days) > MAX_HISTORY_DAYS:
                raise ValueError(
                    f"Date range spans {len(days)} trading days; "
                    f"max is {MAX_HISTORY_DAYS}. Narrow the range or use multiple calls."
                )

            semaphore = asyncio.Semaphore(_REQUEST_SEMAPHORE_LIMIT)

            async def fetch_one(d: dateType) -> list[dict]:
                async with semaphore:
                    return await fetch_settlements(
                        query.symbol,
                        d,
                        product["product_id"],
                        client,
                    )

            results_nested = await asyncio.gather(*(fetch_one(d) for d in days))
            rows = [row for result in results_nested for row in result]

        if query.expiration:
            rows = [r for r in rows if r.get("expiration") == query.expiration]

        if not rows:
            raise EmptyDataError("No settlement data found for the given parameters.")

        return sorted(rows, key=lambda x: (x["date"], x["expiration"]))

    @staticmethod
    def transform_data(
        query: CMEFuturesHistoricalQueryParams, data: list[dict], **kwargs: Any
    ) -> list[CMEFuturesHistoricalData]:
        """Transform the data."""
        return [CMEFuturesHistoricalData.model_validate(d) for d in data]
