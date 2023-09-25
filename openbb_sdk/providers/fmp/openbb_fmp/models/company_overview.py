"""FMP Company Overview Fetcher."""


from typing import Any, Dict, Optional

from openbb_fmp.utils.helpers import get_data_one
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.company_overview import (
    CompanyOverviewData,
    CompanyOverviewQueryParams,
)

# This part is only provided by FMP and not by the other providers for now.


class FMPCompanyOverviewQueryParams(CompanyOverviewQueryParams):
    """FMP Company Overview Query.

    Source: https://site.financialmodelingprep.com/developer/docs/companies-key-stats-free-api/
    """


class FMPCompanyOverviewData(CompanyOverviewData):
    """FMP Company Overview Data."""


class FMPCompanyOverviewFetcher(
    Fetcher[
        FMPCompanyOverviewQueryParams,
        FMPCompanyOverviewData,
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPCompanyOverviewQueryParams:
        """Transform the query params."""
        return FMPCompanyOverviewQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FMPCompanyOverviewQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> Dict:
        """Return the raw data from the FMP endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""

        base_url = "https://financialmodelingprep.com/api/v3"
        url = f"{base_url}/profile/{query.symbol}?apikey={api_key}"

        return get_data_one(url, **kwargs)

    @staticmethod
    def transform_data(  # type: ignore
        data: Dict,
    ) -> FMPCompanyOverviewData:
        """Return the transformed data."""
        return FMPCompanyOverviewData.parse_obj(data)
