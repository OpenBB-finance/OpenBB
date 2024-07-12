"""US Government Treasury Auctions Model."""

# pylint: disable=unused-argument

from typing import Any, Dict, List, Optional

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.treasury_auctions import (
    USTreasuryAuctionsData,
    USTreasuryAuctionsQueryParams,
)


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
        # pylint: disable=import-outside-toplevel
        from pandas import DataFrame  # noqa
        from openbb_core.provider.utils.helpers import (
            get_querystring,
            make_request,
        )  # noqa

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
        r = make_request(url)
        if r.status_code != 200:
            raise OpenBBError(f"{r.status_code}")
        data = DataFrame(r.json())
        results = (
            data.fillna("N/A").replace("", None).replace("N/A", None).to_dict("records")
        )

        return results

    @staticmethod
    def transform_data(
        query: GovernmentUSTreasuryAuctionsQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[GovernementUSTreasuryAuctionsData]:
        """Transform the data."""
        return [GovernementUSTreasuryAuctionsData.model_validate(d) for d in data]
