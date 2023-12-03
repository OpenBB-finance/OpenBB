"""FMP Cash Flow Statement Model."""


from datetime import (
    date as dateType,
    datetime,
)
from typing import Any, Dict, List, Literal, Optional

from openbb_core.provider.abstract.data import ForceInt
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.cash_flow import (
    CashFlowStatementData,
    CashFlowStatementQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_fmp.utils.helpers import create_url, get_data_many
from pydantic import Field, model_validator


class FMPCashFlowStatementQueryParams(CashFlowStatementQueryParams):
    """FMP Cash Flow Statement Query.

    Source: https://financialmodelingprep.com/developer/docs/#Cash-Flow-Statement
    """

    period: Optional[Literal["annual", "quarter"]] = Field(
        default="quarter",
        description=QUERY_DESCRIPTIONS.get("period", ""),
    )
    cik: Optional[str] = Field(
        default=None, description="Central Index Key (CIK) of the company."
    )

    @model_validator(mode="before")
    @classmethod
    def check_symbol_or_cik(cls, values):  # pylint: disable=no-self-argument
        """Validate that either a symbol or CIK is provided."""
        if values.get("symbol") is None and values.get("cik") is None:
            raise ValueError("symbol or cik must be provided")
        return values


class FMPCashFlowStatementData(CashFlowStatementData):
    """FMP Cash Flow Statement Data."""

    __alias_dict__ = {
        "reported_currency": "reportedCurrency",
        "net_cash_used_for_investing_activities": "netCashUsedForInvestingActivites",
        "other_financing_activities": "otherFinancingActivites",
        "net_cash_flow_from_operating_activities": "netCashProvidedByOperatingActivities",
        "purchases_of_marketable_securities": "purchasesOfInvestments",
        "sales_from_maturities_of_investments": "salesMaturitiesOfInvestments",
        "payments_from_acquisitions": "acquisitionsNet",
        "net_cash_flow_from_investing_activities": "netCashUsedForInvestingActivites",
        "net_cash_flow_from_financing_activities": "netCashUsedProvidedByFinancingActivities",
        "other_investing_activities": "otherInvestingActivites",
    }

    reported_currency: str = Field(description="Reported currency in the statement.")
    filling_date: dateType = Field(description="Filling date.")
    accepted_date: datetime = Field(description="Accepted date.")
    calendar_year: Optional[ForceInt] = Field(
        default=None, description="Calendar year."
    )

    change_in_working_capital: Optional[ForceInt] = Field(
        default=None, description="Change in working capital."
    )
    other_working_capital: Optional[ForceInt] = Field(
        default=None, description="Other working capital."
    )
    common_stock_issued: Optional[ForceInt] = Field(
        default=None, description="Common stock issued."
    )
    effect_of_forex_changes_on_cash: Optional[ForceInt] = Field(
        default=None, description="Effect of forex changes on cash."
    )

    cash_at_beginning_of_period: Optional[ForceInt] = Field(
        default=None, description="Cash at beginning of period."
    )
    cash_at_end_of_period: Optional[ForceInt] = Field(
        default=None,
        description="Cash, cash equivalents, and restricted cash at end of period",
    )
    operating_cash_flow: Optional[ForceInt] = Field(
        default=None, description="Operating cash flow."
    )
    capital_expenditure: Optional[ForceInt] = Field(
        default=None, description="Capital expenditure."
    )
    free_cash_flow: Optional[ForceInt] = Field(
        default=None, description="Free cash flow."
    )

    link: Optional[str] = Field(default=None, description="Link to the statement.")
    final_link: Optional[str] = Field(
        default=None, description="Link to the final statement."
    )

    @model_validator(mode="before")
    @classmethod
    def replace_zero(cls, values):  # pylint: disable=no-self-argument
        """Check for zero values and replace with None."""
        return {k: None if v == 0 else v for k, v in values.items()}


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
    def transform_data(
        query: FMPCashFlowStatementQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[FMPCashFlowStatementData]:
        """Return the transformed data."""
        return [FMPCashFlowStatementData.model_validate(d) for d in data]
