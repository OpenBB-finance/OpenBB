"""Deribit Delivery Prices Model."""

from datetime import date as dateType
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


class DeribitDeliveryPricesQueryParams(QueryParams):
    """Deribit Delivery Prices Query.

    Source: https://docs.deribit.com/api-reference/market-data/public-get_delivery_prices
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
    limit: int = Field(
        default=100, description="The number of settlements to return.", ge=1
    )
    offset: int = Field(
        default=0,
        description="How many of the most recent settlements to skip.",
        ge=0,
    )


class DeribitDeliveryPricesData(Data):
    """Deribit Delivery Prices Data."""

    date: dateType = Field(
        description="The session the index delivered on.",
        json_schema_extra={"x-widget_config": {"chartDataType": "category"}},
    )
    index_name: str = Field(
        description="The name of the index.",
        json_schema_extra={"x-widget_config": {"chartDataType": "excluded"}},
    )
    delivery_price: float = Field(
        description="The level the index delivered at.",
        json_schema_extra={
            "x-unit_measurement": "currency",
            "x-widget_config": {"chartDataType": "series"},
        },
    )


class DeribitDeliveryPricesFetcher(
    Fetcher[DeribitDeliveryPricesQueryParams, list[DeribitDeliveryPricesData]]
):
    """Transform the query, extract and transform the data from the Deribit endpoint."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> DeribitDeliveryPricesQueryParams:
        """Transform the query."""
        return DeribitDeliveryPricesQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: DeribitDeliveryPricesQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the Deribit endpoint.

        Raises
        ------
        EmptyDataError
            If none of the indexes has delivered.
        """
        from openbb_deribit.utils.client import gather

        names = [n.strip().lower() for n in query.index_name.split(",") if n.strip()]
        results = await gather(
            [
                (
                    "get_delivery_prices",
                    {
                        "index_name": name,
                        "count": query.limit,
                        "offset": query.offset,
                    },
                )
                for name in names
            ]
        )
        data = [
            {"index_name": name, **record}
            for name, result in zip(names, results)
            if isinstance(result, dict)
            for record in result.get("data") or []
        ]

        if not data:
            raise EmptyDataError(
                f"Deribit published no delivery prices for {', '.join(names)}."
            )

        return data

    @staticmethod
    def transform_data(
        query: DeribitDeliveryPricesQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[DeribitDeliveryPricesData]:
        """Transform the data to the model."""
        return [
            DeribitDeliveryPricesData.model_validate(record)
            for record in sorted(data, key=lambda d: (d["date"], d["index_name"]))
        ]
