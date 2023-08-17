"""FMP Company Overview Fetcher."""


from typing import Any, Dict, List, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.company_overview import (
    CompanyOverviewData,
    CompanyOverviewQueryParams,
)

from openbb_fmp.utils.helpers import get_data_one

# This part is only provided by FMP and not by the other providers for now.


class FMPCompanyOverviewQueryParams(CompanyOverviewQueryParams):
    """FMP Company Overview Query.

    Source: https://site.financialmodelingprep.com/developer/docs/companies-key-stats-free-api/
    """


class FMPCompanyOverviewData(CompanyOverviewData):
    """FMP Company Overview Data."""

    class Config:
        """Pydantic alias config using fields dict."""

        fields = {
            "vol_avg": "volAvg",
            "mkt_cap": "mktCap",
            "last_div": "lastDiv",
            "company_name": "companyName",
            "exchange_short_name": "exchangeShortName",
            "full_time_employees": "fullTimeEmployees",
            "dcf_diff": "dcfDiff",
            "ipo_date": "ipoDate",
            "default_image": "defaultImage",
            "is_etf": "isEtf",
            "is_actively_trading": "isActivelyTrading",
            "is_adr": "isAdr",
            "is_fund": "isFund",
        }


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

        return FMPCompanyOverviewData(**data)
