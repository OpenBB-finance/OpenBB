"""WSJ Asset Performance Losers Model."""

from datetime import datetime
from typing import Any, Dict, List, Optional

import requests
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

    bluegrass_channel: Optional[str] = Field(
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


class WSJLosersFetcher(Fetcher[WSJLosersQueryParams, List[WSJLosersData]]):
    """Transform the query, extract and transform the data from the WSJ endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> WSJLosersQueryParams:
        """Transform query params."""
        return WSJLosersQueryParams(**params)

    @staticmethod
    def extract_data(
        query: WSJLosersQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Get data from WSJ."""
        url = (
            "https://www.wsj.com/market-data/mutualfunds-etfs/etfmovers?id=%7B%22application"
            "%22%3A%22WSJ%22%2C%22etfMover%22%3A%22laggards%22%2C%22count%22%3A25%7D&type="
            "mdc_etfmovers"
        )
        data = requests.get(
            url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10
        ).json()
        return data["data"]["instruments"]

    @staticmethod
    def transform_data(
        query: ETFPerformanceQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[WSJLosersData]:
        """Transform data."""
        data = data[: query.limit]
        data = sorted(
            data,
            key=lambda x: x["percentChange"]
            if query.sort == "desc"
            else -x["percentChange"],
        )
        return [WSJLosersData.model_validate(d) for d in data]
