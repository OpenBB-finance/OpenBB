"""FMP Income Statement Fetcher."""


from typing import Any, Dict, List, Literal, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.income_statement import (
    IncomeStatementData,
    IncomeStatementQueryParams,
)
from pydantic import Field, root_validator

from openbb_fmp.utils.helpers import get_data_many

PeriodType = Literal["annual", "quarter"]


class FMPIncomeStatementQueryParams(IncomeStatementQueryParams):
    """FMP Income Statement QueryParams.

    Source: https://financialmodelingprep.com/developer/docs/#Income-Statement

    Either a Symbol or CIK is required. Symbol is preferred over CIK.
    """

    cik: Optional[str] = Field(
        description="The CIK of the company if no symbol is provided."
    )

    @root_validator()
    def check_symbol_or_cik(cls, values):  # pylint: disable=no-self-argument
        if values.get("symbol") is None and values.get("cik") is None:
            raise ValueError("symbol or cik must be provided")
        return values


class FMPIncomeStatementData(IncomeStatementData):
    class Config:
        fields = {
            "currency": "reportedCurrency",
            "filing_date": "fillingDate",
            "accepted_date": "acceptedDate",
            "calendar_year": "calendarYear",
            "cost_of_revenue": "costOfRevenue",
            "gross_profit": "grossProfit",
            "gross_profit_ratio": "grossProfitRatio",
            "research_and_development_expenses": "researchAndDevelopmentExpenses",
            "general_and_administrative_expenses": "generalAndAdministrativeExpenses",
            "selling_and_marketing_expenses": "sellingAndMarketingExpenses",
            "selling_general_and_administrative_expenses": "sellingGeneralAndAdministrativeExpenses",
            "other_expenses": "otherExpenses",
            "operating_expenses": "operatingExpenses",
            "cost_and_expenses": "costAndExpenses",
            "interest_income": "interestIncome",
            "interest_expense": "interestExpense",
            "depreciation_and_amortization": "depreciationAndAmortization",
            "ebitda": "ebitda",
            "ebitda_ratio": "ebitdaratio",
            "operating_income": "operatingIncome",
            "operating_income_ratio": "operatingIncomeRatio",
            "total_other_income_expenses_net": "totalOtherIncomeExpensesNet",
            "income_before_tax": "incomeBeforeTax",
            "income_before_tax_ratio": "incomeBeforeTaxRatio",
            "income_tax_expense": "incomeTaxExpense",
            "net_income": "netIncome",
            "net_income_ratio": "netIncomeRatio",
            "eps": "eps",
            "eps_diluted": "epsdiluted",
            "weighted_average_shares_outstanding": "weightedAverageShsOut",
            "weighted_average_shares_outstanding_dil": "weightedAverageShsOutDil",
            "final_link": "finalLink",
        }


class FMPIncomeStatementFetcher(
    Fetcher[
        FMPIncomeStatementQueryParams,
        List[FMPIncomeStatementData],
    ]
):
    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPIncomeStatementQueryParams:
        return FMPIncomeStatementQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FMPIncomeStatementQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[FMPIncomeStatementData]:
        api_key = credentials.get("fmp_api_key") if credentials else ""

        query.period = "annual" if query.period == "annually" else "quarter"
        symbol = query.symbol or query.cik
        base_url = "https://financialmodelingprep.com/api/v3"

        url = (
            f"{base_url}/income-statement/{symbol}?"
            f"period={query.period}&limit={query.limit}&apikey={api_key}"
        )

        return get_data_many(url, FMPIncomeStatementData, **kwargs)

    @staticmethod
    def transform_data(
        data: List[FMPIncomeStatementData],
    ) -> List[IncomeStatementData]:
        return [IncomeStatementData.parse_obj(d.dict()) for d in data]
