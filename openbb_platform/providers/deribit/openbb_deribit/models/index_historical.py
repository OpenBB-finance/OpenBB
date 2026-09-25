"""Deribit Index Historical Model."""

from datetime import datetime
from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field, field_validator

from openbb_deribit.utils.constants import (
    INDEX_CHOICES_ENDPOINT,
    SYMBOL_STYLE,
    IndexChartRanges,
)


class DeribitIndexHistoricalQueryParams(QueryParams):
    """Deribit Index Historical Query.

    Source: https://docs.deribit.com/api-reference/market-data/public-get_index_chart_data
    """

    __json_schema_extra__ = {
        "index_name": {
            "multiple_items_allowed": True,
            "x-widget_config": {
                "type": "endpoint",
                "optionsEndpoint": INDEX_CHOICES_ENDPOINT,
                "style": SYMBOL_STYLE,
            },
        }
    }

    index_name: str = Field(
        default="btc_usd",
        description="One or more index names, such as 'btc_usd'.",
    )
    span: IndexChartRanges = Field(
        default="1d", description="How far back the series runs."
    )


class DeribitIndexHistoricalData(Data):
    """Deribit Index Historical Data."""

    date: datetime = Field(
        description="When the level was published.",
        json_schema_extra={"x-widget_config": {"chartDataType": "category"}},
    )
    index_name: str = Field(
        description="The name of the index.",
        json_schema_extra={"x-widget_config": {"chartDataType": "excluded"}},
    )
    price: float = Field(
        description="The level of the index.",
        json_schema_extra={
            "x-unit_measurement": "currency",
            "x-widget_config": {"chartDataType": "series"},
        },
    )

    @field_validator("date", mode="before", check_fields=False)
    @classmethod
    def validate_date(cls, v):
        """Read the timestamp as a datetime."""
        from openbb_deribit.utils.helpers import from_timestamp

        return from_timestamp(v)


class DeribitIndexHistoricalFetcher(
    Fetcher[DeribitIndexHistoricalQueryParams, list[DeribitIndexHistoricalData]]
):
    """Transform the query, extract and transform the data from the Deribit endpoint."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> DeribitIndexHistoricalQueryParams:
        """Transform the query."""
        return DeribitIndexHistoricalQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: DeribitIndexHistoricalQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the Deribit endpoint.

        Raises
        ------
        EmptyDataError
            If none of the indexes published a series.
        """
        from openbb_deribit.utils.client import gather

        names = [n.strip().lower() for n in query.index_name.split(",") if n.strip()]
        results = await gather(
            [
                ("get_index_chart_data", {"index_name": name, "range": query.span})
                for name in names
            ]
        )
        data = [
            {"date": point[0], "index_name": name, "price": point[1]}
            for name, result in zip(names, results)
            if isinstance(result, list)
            for point in result
        ]

        if not data:
            raise EmptyDataError(f"Deribit published no series for {', '.join(names)}.")

        return data

    @staticmethod
    def transform_data(
        query: DeribitIndexHistoricalQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[DeribitIndexHistoricalData]:
        """Transform the data to the model."""
        return [
            DeribitIndexHistoricalData.model_validate(record)
            for record in sorted(data, key=lambda d: (d["date"], d["index_name"]))
        ]
