"""FMP Risk Premium Model."""

from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.risk_premium import (
    RiskPremiumData,
    RiskPremiumQueryParams,
)
from openbb_fmp.utils.helpers import create_url, get_data_many


class FMPRiskPremiumQueryParams(RiskPremiumQueryParams):
    """FMP Risk Premium Query.

    Source: https://site.financialmodelingprep.com/developer/docs/market-risk-premium-api/
    """


class FMPRiskPremiumData(RiskPremiumData):
    """FMP Risk Premium Data."""


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
    async def aextract_data(
        query: FMPRiskPremiumQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""

        url = create_url(4, "market_risk_premium", api_key)

        return await get_data_many(url, **kwargs)

    @staticmethod
    def transform_data(
        query: FMPRiskPremiumQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[FMPRiskPremiumData]:
        """Return the transformed data."""
        return [FMPRiskPremiumData(**item) for item in data]
