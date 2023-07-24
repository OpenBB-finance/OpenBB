"""FMP Risk Premium fetcher."""


from typing import Dict, List, Optional


from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.helpers import data_transformer
from openbb_provider.models.risk_premium import RiskPremiumData, RiskPremiumQueryParams

from openbb_fmp.utils.helpers import create_url, get_data_many


class FMPRiskPremiumQueryParams(RiskPremiumQueryParams):
    """FMP Risk Premium query.

    Source: https://site.financialmodelingprep.com/developer/docs/market-risk-premium-api/

    """


class FMPRiskPremiumData(RiskPremiumData):
    """FMP Risk Premium data."""


class FMPRiskPremiumFetcher(
    Fetcher[
        RiskPremiumQueryParams,
        RiskPremiumData,
        FMPRiskPremiumQueryParams,
        FMPRiskPremiumData,
    ]
):
    @staticmethod
    def transform_query(
        query: RiskPremiumQueryParams, extra_params: Optional[Dict] = None
    ) -> FMPRiskPremiumQueryParams:
        return FMPRiskPremiumQueryParams()

    @staticmethod
    def extract_data(
        query: FMPRiskPremiumQueryParams, api_key: str
    ) -> List[FMPRiskPremiumData]:
        url = create_url(4, "market_risk_premium", api_key)
        return get_data_many(url, FMPRiskPremiumData)

    @staticmethod
    def transform_data(data: List[FMPRiskPremiumData]) -> List[RiskPremiumData]:
        return data_transformer(data, RiskPremiumData)
