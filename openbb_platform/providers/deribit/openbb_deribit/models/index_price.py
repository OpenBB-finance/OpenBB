"""Deribit Index Price Model."""

from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

from openbb_deribit.utils.constants import (
    INDEX_CHOICES_ENDPOINT,
    SYMBOL_STYLE,
)


class DeribitIndexPriceQueryParams(QueryParams):
    """Deribit Index Price Query.

    Source: https://docs.deribit.com/api-reference/market-data/public-get_index_price
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


class DeribitIndexPriceData(Data):
    """Deribit Index Price Data."""

    index_name: str = Field(
        description="The name of the index.",
        json_schema_extra={
            "x-widget_config": {"chartDataType": "category", "pinned": "left"}
        },
    )
    index_price: float | None = Field(
        default=None,
        description="The current level of the index.",
        json_schema_extra={
            "x-unit_measurement": "currency",
            "x-widget_config": {"chartDataType": "series"},
        },
    )
    estimated_delivery_price: float | None = Field(
        default=None,
        description="What instruments on the index would deliver at right now.",
        json_schema_extra={
            "x-unit_measurement": "currency",
            "x-widget_config": {"chartDataType": "excluded"},
        },
    )


class DeribitIndexPriceFetcher(
    Fetcher[DeribitIndexPriceQueryParams, list[DeribitIndexPriceData]]
):
    """Transform the query, extract and transform the data from the Deribit endpoint."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> DeribitIndexPriceQueryParams:
        """Transform the query."""
        return DeribitIndexPriceQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: DeribitIndexPriceQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the Deribit endpoint.

        Raises
        ------
        EmptyDataError
            If none of the indexes published a level.
        """
        from openbb_deribit.utils.client import gather

        names = [n.strip().lower() for n in query.index_name.split(",") if n.strip()]
        results = await gather(
            [("get_index_price", {"index_name": name}) for name in names],
            use_cache=False,
        )

        data = [
            {"index_name": name, **result}
            for name, result in zip(names, results)
            if isinstance(result, dict) and result
        ]

        if not data:
            raise EmptyDataError(f"Deribit published no level for {', '.join(names)}.")

        return data

    @staticmethod
    def transform_data(
        query: DeribitIndexPriceQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[DeribitIndexPriceData]:
        """Transform the data to the model."""
        return [DeribitIndexPriceData.model_validate(record) for record in data]
