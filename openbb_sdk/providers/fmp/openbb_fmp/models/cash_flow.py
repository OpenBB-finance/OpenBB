"""FMP Cash Flow Statement Fetcher."""


from datetime import (
    date as dateType,
    datetime,
)
from typing import Any, Dict, List, Optional

from openbb_fmp.utils.helpers import create_url, get_data_many
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.cash_flow import (
    CashFlowStatementData,
    CashFlowStatementQueryParams,
)
from pydantic import Field, validator


class FMPCashFlowStatementQueryParams(CashFlowStatementQueryParams):
    """FMP Cash Flow Statement Query.

    Source: https://financialmodelingprep.com/developer/docs/#Cash-Flow-Statement
    """

    symbol: str = Field(description="Symbol/CIK of the company.")


class FMPCashFlowStatementData(CashFlowStatementData):
    """FMP Cash Flow Statement Data."""

    class Config:
        """Pydantic alias config using fields dict."""

        fields = {
            "net_cash_flow_from_operating_activities": "netCashProvidedByOperatingActivities",
            "purchases_of_marketable_securities": "purchasesOfInvestments",
            "sales_from_maturities_of_investments": "salesMaturitiesOfInvestments",
            "payments_from_acquisitions": "acquisitionsNet",
            "other_investing_activities": "otherInvestingActivites",
            "net_cash_flow_from_investing_activities": "netCashUsedForInvestingActivites",
            "other_financing_activities": "otherFinancingActivites",
            "net_cash_flow_from_financing_activities": "netCashUsedProvidedByFinancingActivities",
        }

    reported_currency: str = Field(description="Reported currency in the statement.")
    filling_date: dateType = Field(description="Filling date.")
    accepted_date: datetime = Field(description="Accepted date.")
    calendar_year: int = Field(description="Calendar year.")

    change_in_working_capital: Optional[int] = Field(
        description="Change in working capital."
    )
    other_working_capital: Optional[int] = Field(description="Other working capital.")
    common_stock_issued: Optional[int] = Field(description="Common stock issued.")
    effect_of_forex_changes_on_cash: Optional[int] = Field(
        description="Effect of forex changes on cash."
    )

    cash_at_beginning_of_period: Optional[int] = Field(
        description="Cash at beginning of period."
    )
    cash_at_end_of_period: Optional[int] = Field(
        description="Cash, cash equivalents, and restricted cash at end of period"
    )
    operating_cash_flow: Optional[int] = Field(description="Operating cash flow.")
    capital_expenditure: Optional[int] = Field(description="Capital expenditure.")
    free_cash_flow: Optional[int] = Field(description="Free cash flow.")

    link: Optional[str] = Field(description="Link to the statement.")
    final_link: Optional[str] = Field(description="Link to the final statement.")

    @validator("filing_date", pre=True, check_fields=False)
    def filing_date_validate(cls, v):  # pylint: disable=no-self-argument
        """Validate the filing date."""
        return datetime.strptime(v, "%Y-%m-%d").date()

    @validator("accepted_date", pre=True, check_fields=False)
    def accepted_date_validate(cls, v):  # pylint: disable=no-self-argument
        """Validate the accepted date."""
        return datetime.strptime(v, "%Y-%m-%d %H:%M:%S")


class FMPCashFlowStatementFetcher(
    Fetcher[
        FMPCashFlowStatementQueryParams,
        List[FMPCashFlowStatementData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPCashFlowStatementQueryParams:
        """Transform the query params."""
        return FMPCashFlowStatementQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FMPCashFlowStatementQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""

        url = create_url(
            3, f"cash-flow-statement/{query.symbol}", api_key, query, ["symbol"]
        )

        return get_data_many(url, **kwargs)

    @staticmethod
    def transform_data(data: List[Dict]) -> List[FMPCashFlowStatementData]:
        """Return the transformed data."""
        return [FMPCashFlowStatementData.parse_obj(d) for d in data]
