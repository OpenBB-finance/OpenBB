"""SEC Filings fetcher."""


from typing import Any, Dict, List, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.models.sec_filings import SECFilingsData, SECFilingsQueryParams

from openbb_fmp.utils.helpers import create_url, get_data_many


class FMPSECFilingsQueryParams(SECFilingsQueryParams):
    """FMP SEC Filings Query.

    Source: https://site.financialmodelingprep.com/developer/docs/sec-filings-api/
    """


class FMPSECFilingsData(SECFilingsData):
    """FMP SEC Filings Data."""

    class Config:
        fields = {
            "filling_date": "fillingDate",
            "accepted_date": "acceptedDate",
            "final_link": "finalLink",
        }


class FMPSECFilingsFetcher(
    Fetcher[
        SECFilingsQueryParams,
        List[SECFilingsData],
        FMPSECFilingsQueryParams,
        List[FMPSECFilingsData],
    ]
):
    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPSECFilingsQueryParams:
        return FMPSECFilingsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FMPSECFilingsQueryParams, credentials: Optional[Dict[str, str]]
    ) -> List[FMPSECFilingsData]:
        api_key = credentials.get("fmp_api_key") if credentials else ""

        url = create_url(
            3, f"sec_filings/{query.symbol}", api_key, query, exclude=["symbol"]
        )

        return get_data_many(url, FMPSECFilingsData)

    @staticmethod
    def transform_data(data: List[FMPSECFilingsData]) -> List[SECFilingsData]:
        return [SECFilingsData.parse_obj(d.dict()) for d in data]
