"""Intrinio Share Statistics Model."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.share_statistics import (
    ShareStatisticsData,
    ShareStatisticsQueryParams,
)
from openbb_core.provider.utils.helpers import (
    ClientResponse,
    amake_requests,
)
from pydantic import Field


class IntrinioShareStatisticsQueryParams(ShareStatisticsQueryParams):
    """Intrinio Share Statistics Query.

    Source: https://data.intrinio.com/data-tag/adjweightedavebasicdilutedsharesos
            https://data.intrinio.com/data-tag/weightedavebasicdilutedsharesos
            https://data.intrinio.com/data-tag/public_float
    """


class IntrinioShareStatisticsData(ShareStatisticsData):
    """Intrinio Share Statistics Data."""

    __alias_dict__ = {
        "outstanding_shares": "weightedavebasicdilutedsharesos",
        "adjusted_outstanding_shares": "adjweightedavebasicdilutedsharesos",
    }

    adjusted_outstanding_shares: Optional[float] = Field(
        default=None,
        description="Total number of shares of a publicly-traded company, adjusted for splits.",
    )
    public_float: Optional[float] = Field(
        default=None,
        description="Aggregate market value of the shares of a publicly-traded company.",
    )


class IntrinioShareStatisticsFetcher(
    Fetcher[
        IntrinioShareStatisticsQueryParams,
        List[IntrinioShareStatisticsData],
    ]
):
    """Transform the query, extract and transform the data from the Intrinio endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> IntrinioShareStatisticsQueryParams:
        """Transform the query params."""
        return IntrinioShareStatisticsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: IntrinioShareStatisticsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the Intrinio endpoint."""
        api_key = credentials.get("intrinio_api_key") if credentials else ""
        data = {"symbol": query.symbol, "date": datetime.now().date()}

        tags = [
            "public_float",
            "weightedavebasicdilutedsharesos",
            "adjweightedavebasicdilutedsharesos",
        ]

        urls = [
            f"https://api-v2.intrinio.com/companies/{query.symbol}/data_point/{tag}/number?api_key={api_key}"
            for tag in tags
        ]

        async def callback(response: ClientResponse, _: Any) -> Dict:
            """Return the response."""
            return {response.url.parts[-2]: await response.json()}

        for result in await amake_requests(urls, callback, **kwargs):
            data.update(result)

        return [data]

    @staticmethod
    def transform_data(
        query: IntrinioShareStatisticsQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[IntrinioShareStatisticsData]:
        """Return the transformed data."""
        return [IntrinioShareStatisticsData.model_validate(d) for d in data]
