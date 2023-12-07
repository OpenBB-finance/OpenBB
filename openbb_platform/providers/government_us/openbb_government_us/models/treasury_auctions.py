"""US Government Treasury Auctions Model."""

from typing import Any, Dict, List, Optional

import pandas as pd
import requests
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.treasury_auctions import (
    USTreasuryAuctionsData,
    USTreasuryAuctionsQueryParams,
)
from openbb_core.provider.utils.helpers import get_querystring


class GovernmentUSTreasuryAuctionsQueryParams(USTreasuryAuctionsQueryParams):
    """US Government Treasury Auctions Query.

    Source: https://www.treasurydirect.gov/
    """

    __alias_dict__ = {
        "start_date": "startDate",
        "end_date": "endDate",
        "security_type": "type",
        "page_size": "pagesize",
        "page_num": "pagenum",
    }


class GovernementUSTreasuryAuctionsData(USTreasuryAuctionsData):
    """US Government Treasury Auctions Data."""


class GovernmentUSTreasuryAuctionsFetcher(
    Fetcher[
        GovernmentUSTreasuryAuctionsQueryParams,
        List[GovernementUSTreasuryAuctionsData],
    ]
):
    """Transform the query, extract and transform the data from the us treasury endpoints."""

    @staticmethod
    def transform_query(
        params: Dict[str, Any]
    ) -> GovernmentUSTreasuryAuctionsQueryParams:
        """Transform query params."""
        return GovernmentUSTreasuryAuctionsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: GovernmentUSTreasuryAuctionsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Extract the raw data from Treasury Direct API."""
        base_url = "https://www.treasurydirect.gov/TA_WS/securities/search?"

        _query = query.model_dump()
        _query["startDate"] = (
            _query["startDate"].strftime("%m/%d/%Y") if query.start_date else None
        )
        _query["endDate"] = (
            _query["endDate"].strftime("%m/%d/%Y") if _query["endDate"] else None
        )
        query_string = get_querystring(_query, [])

        url = base_url + query_string + "&format=json"
        r = requests.get(url, timeout=5)
        if r.status_code != 200:
            raise RuntimeError(r.status_code)
        data = pd.DataFrame(r.json())
        results = data.replace("", None).convert_dtypes().to_dict("records")

        return results

    @staticmethod
    def transform_data(
        query: GovernmentUSTreasuryAuctionsQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[GovernementUSTreasuryAuctionsData]:
        """Transform the data."""
        return [GovernementUSTreasuryAuctionsData.model_validate(d) for d in data]
