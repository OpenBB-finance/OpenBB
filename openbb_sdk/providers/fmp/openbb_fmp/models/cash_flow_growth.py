"""FMP Cash Flow Statement Growth Fetcher."""


from datetime import datetime
from typing import Any, Dict, List, Optional

from openbb_fmp.utils.helpers import create_url, get_data_many
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.cash_flow_growth import (
    CashFlowStatementGrowthData,
    CashFlowStatementGrowthQueryParams,
)
from pydantic import validator


class FMPCashFlowStatementGrowthQueryParams(CashFlowStatementGrowthQueryParams):
    """FMP Cash Flow Statement Growth QueryParams.

    Source: https://site.financialmodelingprep.com/developer/docs/financial-statements-growth-api/
    """


class FMPCashFlowStatementGrowthData(CashFlowStatementGrowthData):
    """FMP Cash Flow Statement Growth Data."""

    class Config:
        """Pydantic alias config using fields Dict."""

        fields = {
            "growth_net_cash_provided_by_operating_activities": "growthNetCashProvidedByOperatingActivites",
            "growth_other_investing_activities": "growthOtherInvestingActivites",
            "growth_net_cash_used_for_investing_activities": "growthNetCashUsedForInvestingActivites",
            "growth_other_financing_activities": "growthOtherFinancingActivites",
        }

    @validator("date", pre=True, check_fields=False)
    def date_validate(cls, v):  # pylint: disable=E0213
        """Return the date as a datetime object."""
        return datetime.strptime(v, "%Y-%m-%d")


class FMPCashFlowStatementGrowthFetcher(
    Fetcher[
        FMPCashFlowStatementGrowthQueryParams,
        List[FMPCashFlowStatementGrowthData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(
        params: Dict[str, Any]
    ) -> FMPCashFlowStatementGrowthQueryParams:
        """Transform the query params."""
        return FMPCashFlowStatementGrowthQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FMPCashFlowStatementGrowthQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Transform the query, extract and transform the data from the FMP endpoints."""
        api_key = credentials.get("fmp_api_key") if credentials else ""

        url = create_url(
            3, f"cash-flow-statement-growth/{query.symbol}", api_key, query, ["symbol"]
        )

        return get_data_many(url, **kwargs)

    @staticmethod
    def transform_data(data: List[Dict]) -> List[FMPCashFlowStatementGrowthData]:
        """Return the transformed data."""
        return [FMPCashFlowStatementGrowthData.parse_obj(d) for d in data]
