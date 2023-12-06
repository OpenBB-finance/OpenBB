"""FMP Discovery Filings Model."""

import math
from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.discovery_filings import (
    DiscoveryFilingsData,
    DiscoveryFilingsQueryParams,
)
from openbb_core.provider.utils.helpers import get_querystring
from openbb_fmp.utils.helpers import get_data_many
from pydantic import Field


class FMPDiscoveryFilingsQueryParams(DiscoveryFilingsQueryParams):
    """FMP Discovery Filings Query.

    Source: https://site.financialmodelingprep.com/developer/docs/sec-rss-feeds-api/
    """

    __alias_dict__ = {
        "start_date": "from",
        "end_date": "to",
        "form_type": "type",
    }

    is_done: Optional[bool] = Field(
        default=None,
        description="Flag for whether or not the filing is done.",
        alias="isDone",
    )


class FMPDiscoveryFilingsData(DiscoveryFilingsData):
    """FMP Discovery Filings Data."""

    __alias_dict__ = {"symbol": "ticker"}


class FMPDiscoveryFilingsFetcher(
    Fetcher[
        FMPDiscoveryFilingsQueryParams,
        List[FMPDiscoveryFilingsData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPDiscoveryFilingsQueryParams:
        """Transform the query."""
        return FMPDiscoveryFilingsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FMPDiscoveryFilingsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""
        data: List[Dict] = []

        base_url = "https://financialmodelingprep.com/api/v4/rss_feed"
        query_str = get_querystring(query.model_dump(by_alias=True), ["limit"])

        # FMP only allows 1000 results per page
        pages = math.ceil(query.limit / 1000)
        for page in range(pages):
            query_str += f"&page={page}"
            url = f"{base_url}?{query_str}&apikey={api_key}"
            response = get_data_many(url, **kwargs)
            data.extend(response)

        return data[: query.limit]

    @staticmethod
    def transform_data(
        query: FMPDiscoveryFilingsQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[FMPDiscoveryFilingsData]:
        """Return the transformed data."""
        return [FMPDiscoveryFilingsData.model_validate(d) for d in data]
