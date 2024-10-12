from logging import warn
from typing import Dict, Any, Optional, List

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.house_disclosure_rss_feed import HouseDisclosureRSSFeedQueryParams, \
    HouseDisclosureRSSFeedData
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_core.provider.utils.helpers import amake_request
from openbb_fmp.utils.helpers import create_url, response_callback


class FMPHouseDisclosureRSSFeedQueryParams(HouseDisclosureRSSFeedQueryParams):
    """FMP House Disclosure RSS Feed Query Parameters.

    Source: https://financialmodelingprep.com/api/v4/senate-disclosure-rss-feed
    """

    pass


class FMPHouseDisclosureRSSFeedData(HouseDisclosureRSSFeedData):
    """FMP House Disclosure RSS Feed Data Model."""


class FMPHouseDisclosureRSSFeedFetcher(
    Fetcher[
        FMPHouseDisclosureRSSFeedQueryParams,
        List[FMPHouseDisclosureRSSFeedData],
    ]
):
    """Fetches and transforms data from the FMP House Disclosure RSS Feed endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPHouseDisclosureRSSFeedQueryParams:
        """Transform the query params."""
        return FMPHouseDisclosureRSSFeedQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FMPHouseDisclosureRSSFeedQueryParams,
        credentials: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP House Disclosure RSS Feed endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""

        results: List[Dict] = []

        async def get_data(page):
            """Get data for one page."""
            url = create_url(4, f"senate-disclosure-rss-feed?page={page}", api_key)
            result = await amake_request(
                url, response_callback=response_callback, **kwargs
            )
            if not result or len(result) == 0:
                warn(f"Page Error: No data found for page {page}")
            if result:
                results.extend(result)

        await get_data(query.page)

        if not results:
            raise EmptyDataError("No data returned for the given page.")

        return results

    @staticmethod
    def transform_data(
        query: FMPHouseDisclosureRSSFeedQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[FMPHouseDisclosureRSSFeedData]:
        """Return the transformed data."""
        return [FMPHouseDisclosureRSSFeedData(**d) for d in data]
