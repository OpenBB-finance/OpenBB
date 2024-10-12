"""Senate Trading RSS Feed Model."""

from typing import Any, Dict, List, Optional
from warnings import warn

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.senate_trading_rss_feed import (
    SenateTradingRSSFeedData,
    SenateTradingRSSFeedQueryParams,
)
from openbb_core.provider.utils.helpers import amake_request
from openbb_fmp.utils.helpers import create_url, response_callback

from openbb_core.provider.utils.errors import EmptyDataError



class FMPSenateTradingRSSFeedQueryParams(SenateTradingRSSFeedQueryParams):
    """Senate Trading RSS Feed Query.

    Source: https://financialmodelingprep.com/api/v4/senate-trading-rss-feed
    """


class FMPSenateTradingRSSFeedData(SenateTradingRSSFeedData):
    """Senate Trading RSS Feed Data."""


class FMPSenateTradingRSSFeedFetcher(
    Fetcher[
        FMPSenateTradingRSSFeedQueryParams,
        List[FMPSenateTradingRSSFeedData],
    ]
):
    """Transform the query, extract and transform the data from the Senate Trading RSS Feed endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPSenateTradingRSSFeedQueryParams:
        """Transform the query params."""
        return FMPSenateTradingRSSFeedQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FMPSenateTradingRSSFeedQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the Senate Trading RSS Feed endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""

        results: List[dict] = []

        async def get_one():
            """Get data for one page."""
            url = create_url(4, "senate-trading-rss-feed", api_key, query)
            result = await amake_request(
                url, response_callback=response_callback, **kwargs
            )
            if not result or len(result) == 0:
                warn(f"Page Error: No data found for page {query.page}")
            if result:
                results.extend(result)

        await get_one()

        if not results:
            raise EmptyDataError("No data returned for the given page.")

        return results

    @staticmethod
    def transform_data(
        query: FMPSenateTradingRSSFeedQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[FMPSenateTradingRSSFeedData]:
        """Return the transformed data."""
        return [FMPSenateTradingRSSFeedData.model_validate(d) for d in data]
