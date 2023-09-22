"""SEC Filings fetcher."""


from typing import Any, Dict, List, Optional

from openbb_fmp.utils.helpers import create_url, get_data_many
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.sec_filings import (
    SECFilingsData,
    SECFilingsQueryParams,
)


class FMPSECFilingsQueryParams(SECFilingsQueryParams):
    """FMP SEC Filings Query.

    Source: https://site.financialmodelingprep.com/developer/docs/sec-filings-api/
    """


class FMPSECFilingsData(SECFilingsData):
    """FMP SEC Filings Data."""


class FMPSECFilingsFetcher(
    Fetcher[
        FMPSECFilingsQueryParams,
        List[FMPSECFilingsData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPSECFilingsQueryParams:
        """Transform the query params."""
        return FMPSECFilingsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FMPSECFilingsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""

        url = create_url(
            3, f"sec_filings/{query.symbol}", api_key, query, exclude=["symbol"]
        )

        return get_data_many(url, **kwargs)

    @staticmethod
    def transform_data(data: List[Dict]) -> List[FMPSECFilingsData]:
        """Return the transformed data."""
        return [FMPSECFilingsData.parse_obj(d) for d in data]
