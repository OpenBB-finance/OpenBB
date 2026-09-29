"""Deribit APR History Model."""

from datetime import date as dateType
from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field, field_validator

from openbb_deribit.utils.constants import AprCurrencies


class DeribitAprHistoryQueryParams(QueryParams):
    """Deribit APR History Query.

    Source: https://docs.deribit.com/api-reference/market-data/public-get_apr_history
    """

    currency: AprCurrencies = Field(
        default="usde", description="The yield-bearing currency."
    )
    limit: int = Field(default=365, description="The number of days to return.", ge=1)


class DeribitAprHistoryData(Data):
    """Deribit APR History Data."""

    __alias_dict__ = {"date": "day"}

    date: dateType = Field(
        description="The day the rate applied to.",
        json_schema_extra={"x-widget_config": {"chartDataType": "category"}},
    )
    currency: str = Field(
        description="The currency earning the rate.",
        json_schema_extra={"x-widget_config": {"chartDataType": "excluded"}},
    )
    apr: float = Field(
        description="The annual percentage rate the currency earned.",
        json_schema_extra={
            "x-unit_measurement": "percent",
            "x-widget_config": {
                "headerName": "APR",
                "chartDataType": "series",
            },
        },
    )

    @field_validator("date", mode="before", check_fields=False)
    @classmethod
    def validate_date(cls, v):
        """Read the day number as a date."""
        from openbb_deribit.utils.helpers import from_day_number

        return from_day_number(v)


class DeribitAprHistoryFetcher(
    Fetcher[DeribitAprHistoryQueryParams, list[DeribitAprHistoryData]]
):
    """Transform the query, extract and transform the data from the Deribit endpoint."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> DeribitAprHistoryQueryParams:
        """Transform the query."""
        return DeribitAprHistoryQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: DeribitAprHistoryQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the Deribit endpoint.

        Raises
        ------
        EmptyDataError
            If the currency earned nothing over the span.
        """
        from openbb_deribit.utils.client import request

        result = await request(
            "get_apr_history",
            {"currency": query.currency.lower(), "limit": query.limit},
        )
        data = [
            {"currency": query.currency.upper(), **record}
            for record in (result or {}).get("data") or []
        ]

        if not data:
            raise EmptyDataError(
                f"Deribit published no yield history for {query.currency.upper()}."
            )

        return data

    @staticmethod
    def transform_data(
        query: DeribitAprHistoryQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[DeribitAprHistoryData]:
        """Transform the data to the model."""
        return [
            DeribitAprHistoryData.model_validate(record)
            for record in sorted(data, key=lambda d: d.get("day") or 0)
        ]
