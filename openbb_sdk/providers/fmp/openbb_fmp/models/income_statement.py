"""FMP Income Statement Fetcher."""


from typing import Any, Dict, List, Literal, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.models.income_statement import (
    IncomeStatementData,
    IncomeStatementQueryParams,
)
from pydantic import Field, root_validator

from openbb_fmp.utils.helpers import create_url, get_data_many

PeriodType = Literal["annual", "quarter"]


class FMPIncomeStatementQueryParams(IncomeStatementQueryParams):
    """FMP Income Statement QueryParams.

    Source: https://financialmodelingprep.com/developer/docs/#Income-Statement
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
            "cost_of_revenue": "costOfRevenue",
            "gross_profit": "grossProfit",
            "research_and_development_expenses": "researchAndDevelopmentExpenses",
            "general_and_administrative_expenses": "generalAndAdministrativeExpenses",
            "selling_and_marketing_expenses": "sellingAndMarketingExpenses",
            "selling_general_and_administrative_expenses": "sellingGeneralAndAdministrativeExpenses",
            "other_expenses": "otherExpenses",
            "operating_expenses": "operatingExpenses",
            "depreciation_and_amortization": "depreciationAndAmortization",
            "operating_income": "operatingIncome",
            "interest_income": "interestIncome",
            "interest_expense": "interestExpense",
            "total_other_income_expenses_net": "totalOtherIncomeExpensesNet",
            "income_before_tax": "incomeBeforeTax",
            "income_tax_expense": "incomeTaxExpense",
            "net_income": "netIncome",
            "eps_diluted": "epsdiluted",
            "weighted_average_shares_outstanding": "weightedAverageShsOut",
            "weighted_average_shares_outstanding_dil": "weightedAverageShsOutDil",
        }

    calendarYear: Optional[int]
    grossProfitRatio: Optional[float]
    ebitdaratio: Optional[float]
    operatingIncomeRatio: Optional[float]
    incomeBeforeTaxRatio: Optional[float]
    netIncomeRatio: Optional[float]
    link: Optional[str]
    finalLink: Optional[str]


class FMPIncomeStatementFetcher(
    Fetcher[
        IncomeStatementQueryParams,
        IncomeStatementData,
        FMPIncomeStatementQueryParams,
        FMPIncomeStatementData,
    ]
):
    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPIncomeStatementQueryParams:
        return FMPIncomeStatementQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FMPIncomeStatementQueryParams, credentials: Optional[Dict[str, str]]
    ) -> List[FMPIncomeStatementData]:
        api_key = credentials.get("fmp_api_key") if credentials else ""

        url = create_url(
            3, f"income-statement/{query.symbol}", api_key, query, ["symbol"]
        )
        return get_data_many(url, FMPIncomeStatementData)

    @staticmethod
    def transform_data(
        data: List[FMPIncomeStatementData],
    ) -> List[FMPIncomeStatementData]:
        return data
