"""FMP Risk Premium fetcher."""


from typing import Any, Dict, List, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.models.risk_premium import RiskPremiumData, RiskPremiumQueryParams

from openbb_fmp.utils.helpers import create_url, get_data_many


class FMPRiskPremiumQueryParams(RiskPremiumQueryParams):
    """FMP Risk Premium query.

    Source: https://site.financialmodelingprep.com/developer/docs/market-risk-premium-api/
    """


class FMPRiskPremiumData(RiskPremiumData):
    """FMP Risk Premium data."""

    class Config:
        fields = {
            "total_equity_risk_premium": "totalEquityRiskPremium",
            "country_risk_premium": "countryRiskPremium",
        }


class FMPRiskPremiumFetcher(
    Fetcher[
        RiskPremiumQueryParams,
        RiskPremiumData,
        FMPRiskPremiumQueryParams,
        FMPRiskPremiumData,
    ]
):
    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPRiskPremiumQueryParams:
        return FMPRiskPremiumQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FMPRiskPremiumQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any
    ) -> List[FMPRiskPremiumData]:
        api_key = credentials.get("fmp_api_key") if credentials else ""

        url = create_url(4, "market_risk_premium", api_key)

        return get_data_many(url, FMPRiskPremiumData)

    @staticmethod
    def transform_data(data: List[FMPRiskPremiumData]) -> List[FMPRiskPremiumData]:
        return data
