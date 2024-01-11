"""US Government Treasury Annoucements."""

from datetime import (
    datetime,
    timedelta,
)
from typing import Any, Dict, List, Optional

import pandas as pd
import requests
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.treasury_auctions import (
    USTreasuryAuctionsData,
    USTreasuryAnnoucementsQueryParams,
)
from openbb_provider.utils.helpers import get_querystring


class GovernmentUSTreasuryAnnoucementsQueryParams(USTreasuryAnnoucementsQueryParams):
    """
    US Treasury Annoucements Query Params

    Source: https://www.treasurydirect.gov/
    """

    __alias_dict__ = {
        "start_date": "startDate",
        "end_date": "endDate",
        "security_type": "type",
        "page_size": "pagesize",
        "page_num": "pagenum",
    }


class GovernementUSTreasuryAnnoucementsData(USTreasuryAuctionsData):
    """US Treasury Annoucements Data."""


class GovernmentUSTreasuryAnnoucementsFetcher(
    Fetcher[
        GovernmentUSTreasuryAnnoucementsQueryParams,
        List[GovernementUSTreasuryAnnoucementsData],
    ]
):
    """US Treasury Annoucements Fetcher."""

    @staticmethod
    def transform_query(
        params: Dict[str, Any]
    ) -> GovernmentUSTreasuryAnnoucementsQueryParams:
        """Transform query params."""
        return GovernmentUSTreasuryAnnoucementsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: GovernmentUSTreasuryAnnoucementsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Extract the raw data from Treasury Direct API."""

        "https://www.treasurydirect.gov/TA_WS/securities/announced?format=json&type=FRN"
        base_url = "https://www.treasurydirect.gov/TA_WS/securities/announced?"

        query_string = get_querystring(query.model_dump(), [])

        url = base_url + query_string + "&format=json"
        r = requests.get(url, timeout=5)
        if r.status_code != 200:
            raise RuntimeError(r.status_code)
        data = pd.DataFrame(r.json())
        results = data.replace("", None).convert_dtypes().to_dict("records")

        return results

    @staticmethod
    def transform_data(
        query: GovernmentUSTreasuryAnnoucementsQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[GovernementUSTreasuryAnnoucementsData]:
        """Transform data into the model"""
        return [GovernementUSTreasuryAnnoucementsData.model_validate(d) for d in data]
