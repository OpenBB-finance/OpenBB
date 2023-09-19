"""FMP Risk Premium fetcher."""


from typing import Any, Dict, List, Optional

from openbb_fmp.utils.helpers import create_url, get_data_many
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.risk_premium import (
    RiskPremiumData,
    RiskPremiumQueryParams,
)


class FMPRiskPremiumQueryParams(RiskPremiumQueryParams):
    """FMP Risk Premium query.

    Source: https://site.financialmodelingprep.com/developer/docs/market-risk-premium-api/
    """


class FMPRiskPremiumData(RiskPremiumData):
    """FMP Risk Premium data."""


class FMPRiskPremiumFetcher(
    Fetcher[
        FMPRiskPremiumQueryParams,
        List[FMPRiskPremiumData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPRiskPremiumQueryParams:
        """Transform the query params."""
        return FMPRiskPremiumQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FMPRiskPremiumQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""

        url = create_url(4, "market_risk_premium", api_key)

        return get_data_many(url, **kwargs)

    @staticmethod
    def transform_data(data: List[Dict]) -> List[FMPRiskPremiumData]:
        """Return the transformed data."""
        return [FMPRiskPremiumData(**item) for item in data]
