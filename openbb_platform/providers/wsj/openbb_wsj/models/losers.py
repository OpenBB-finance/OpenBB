"""WSJ Asset Performance Losers Model."""

# pylint: disable=unused-argument

from datetime import datetime
from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.etf_performance import (
    ETFPerformanceData,
    ETFPerformanceQueryParams,
)
from pydantic import Field, field_validator


class WSJLosersQueryParams(ETFPerformanceQueryParams):
    """WSJ Asset Performance Losers Query.

    Source: https://www.wsj.com/market-data/mutualfunds-etfs/etfmovers
    """


class WSJLosersData(ETFPerformanceData):
    """WSJ Asset Performance Losers Data."""

    __alias_dict__ = {
        "symbol": "ticker",
        "last_price": "lastPrice",
        "percent_change": "percentChange",
        "net_change": "priceChange",
        "date": "timestamp",
    }

    bluegrass_channel: str | None = Field(
        description="Bluegrass channel.", default=None
    )
    country: str = Field(
        description="Country of the entity.",
    )
    mantissa: int = Field(
        description="Mantissa.",
    )
    type: str = Field(
        description="Type of the entity.",
    )
    formatted_price: str = Field(
        description="Formatted price.",
    )
    formatted_volume: str = Field(
        description="Formatted volume.",
    )
    formatted_price_change: str = Field(
        description="Formatted price change.",
    )
    formatted_percent_change: str = Field(
        description="Formatted percent change.",
    )
    url: str = Field(
        description="The source url.",
    )

    @field_validator("date", mode="before", check_fields=False)
    def date_validate(cls, v):  # pylint: disable=E0213
        """Return the datetime object from the date string."""
        return datetime.strptime(v[:10], "%Y-%m-%d").date()


class WSJLosersFetcher(Fetcher[WSJLosersQueryParams, list[WSJLosersData]]):
    """Transform the query, extract and transform the data from the WSJ endpoints."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> WSJLosersQueryParams:
        """Transform query params."""
        return WSJLosersQueryParams(**params)

    @staticmethod
    def extract_data(
        query: WSJLosersQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Get data from WSJ."""
        # pylint: disable=import-outside-toplevel
        from openbb_core.provider.utils.helpers import make_request

        url = (
            "https://www.wsj.com/market-data/mutualfunds-etfs/etfmovers?id=%7B%22application"
            "%22%3A%22WSJ%22%2C%22etfMover%22%3A%22laggards%22%2C%22count%22%3A25%7D&type="
            "mdc_etfmovers"
        )
        data = make_request(url).json()

        return data["data"]["instruments"]

    @staticmethod
    def transform_data(
        query: ETFPerformanceQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[WSJLosersData]:
        """Transform data."""
        data = data[: query.limit]
        data = sorted(
            data,
            key=lambda x: (
                x["percentChange"] if query.sort == "desc" else -x["percentChange"]
            ),
        )
        return [WSJLosersData.model_validate(d) for d in data]
