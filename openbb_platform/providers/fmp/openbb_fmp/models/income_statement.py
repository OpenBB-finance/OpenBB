"""FMP Income Statement Model."""

from datetime import (
    date as dateType,
    datetime,
)
from typing import Any, Dict, List, Literal, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.income_statement import (
    IncomeStatementData,
    IncomeStatementQueryParams,
)
from openbb_fmp.utils.helpers import get_data_many
from pydantic import Field, model_validator

PeriodType = Literal["annual", "quarter"]


class FMPIncomeStatementQueryParams(IncomeStatementQueryParams):
    """FMP Income Statement Query.

    Source: https://financialmodelingprep.com/developer/docs/#Income-Statement
    """

    cik: Optional[str] = Field(
        default=None, description="The CIK of the company if no symbol is provided."
    )

    @model_validator(mode="before")
    @classmethod
    def check_symbol_or_cik(cls, values):  # pylint: disable=no-self-argument
        """Validate that either a symbol or CIK is provided."""
        if values.get("symbol") is None and values.get("cik") is None:
            raise ValueError("symbol or cik must be provided")
        return values


class FMPIncomeStatementData(IncomeStatementData):
    """FMP Income Statement Data."""

    __alias_dict__ = {
        "reported_currency": "reportedCurrency",
        "ebitda_ratio": "ebitdaratio",
        "eps_diluted": "epsdiluted",
        "weighted_average_shares_outstanding": "weightedAverageShsOut",
        "weighted_average_shares_outstanding_dil": "weightedAverageShsOutDil",
        "filling_date": "fillingDate",
    }

    reported_currency: Optional[str] = Field(
        default=None, description="Reporting currency."
    )
    filling_date: Optional[dateType] = Field(default=None, description="Filling date.")
    accepted_date: Optional[datetime] = Field(
        default=None, description="Accepted date."
    )
    calendar_year: Optional[int] = Field(default=None, description="Calendar year.")

    cost_of_revenue: Optional[float] = Field(
        default=None, description="Cost of revenue."
    )
    gross_profit: Optional[float] = Field(default=None, description="Gross profit.")
    gross_profit_ratio: Optional[float] = Field(
        default=None, description="Gross profit ratio."
    )
    research_and_development_expenses: Optional[float] = Field(
        default=None, description="Research and development expenses."
    )
    general_and_administrative_expenses: Optional[float] = Field(
        default=None, description="General and administrative expenses."
    )
    selling_and_marketing_expenses: Optional[float] = Field(
        default=None, description="Selling and marketing expenses."
    )
    selling_general_and_administrative_expenses: Optional[float] = Field(
        default=None, description="Selling, general and administrative expenses."
    )
    other_expenses: Optional[float] = Field(default=None, description="Other expenses.")

    operating_expenses: Optional[float] = Field(
        default=None, description="Operating expenses."
    )
    depreciation_and_amortization: Optional[float] = Field(
        default=None, description="Depreciation and amortization."
    )
    ebitda_ratio: Optional[float] = Field(default=None, description="EBIDTA ratio.")
    operating_income: Optional[float] = Field(
        default=None, description="Operating income."
    )
    operating_income_ratio: Optional[float] = Field(
        default=None, description="Operating income ratio."
    )
    interest_income: Optional[float] = Field(
        default=None, description="Interest income."
    )
    interest_expense: Optional[float] = Field(
        default=None, description="Interest expense."
    )

    total_other_income_expenses_net: Optional[float] = Field(
        default=None, description="Total other income expenses net."
    )
    income_before_tax: Optional[float] = Field(
        default=None, description="Income before tax."
    )
    income_before_tax_ratio: Optional[float] = Field(
        default=None, description="Income before tax ratio."
    )
    income_tax_expense: Optional[float] = Field(
        default=None, description="Income tax expense."
    )
    net_income: Optional[float] = Field(default=None, description="Net income.")
    net_income_ratio: Optional[float] = Field(
        default=None, description="Net income ratio."
    )

    link: Optional[str] = Field(
        default=None, description="Link to the income statement."
    )
    final_link: Optional[str] = Field(
        default=None, description="Final link to the income statement."
    )

    @model_validator(mode="before")
    @classmethod
    def replace_zero(cls, values):  # pylint: disable=no-self-argument
        """Check for zero values and replace with None."""
        return {k: None if v == 0 else v for k, v in values.items()}


class FMPIncomeStatementFetcher(
    Fetcher[
        FMPIncomeStatementQueryParams,
        List[FMPIncomeStatementData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPIncomeStatementQueryParams:
        """Transform the query params."""
        return FMPIncomeStatementQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FMPIncomeStatementQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""

        symbol = query.symbol
        base_url = "https://financialmodelingprep.com/api/v3"

        url = (
            f"{base_url}/income-statement/{symbol}?"
            f"period={query.period}&limit={query.limit}&apikey={api_key}"
        )

        return get_data_many(url, **kwargs)

    @staticmethod
    def transform_data(
        query: FMPIncomeStatementQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[FMPIncomeStatementData]:
        """Return the transformed data."""
        return [FMPIncomeStatementData.model_validate(d) for d in data]
