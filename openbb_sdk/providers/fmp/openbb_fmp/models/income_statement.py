"""FMP Income Statement Fetcher."""


from datetime import (
    date as dateType,
    datetime,
)
from typing import Any, Dict, List, Literal, Optional

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.models.income_statement import (
    IncomeStatementData,
    IncomeStatementQueryParams,
)
from pydantic import Field, NonNegativeInt, root_validator

from openbb_fmp.utils.helpers import create_url, get_data_many

PeriodType = Literal["annual", "quarter"]


class FMPIncomeStatementQueryParams(QueryParams):
    """FMP Income Statement QueryParams.

    Source: https://financialmodelingprep.com/developer/docs/#Income-Statement

    Parameter
    ---------
    symbol : Optional[str]
        The symbol of the company if no CIK is provided.
    cik : Optional[str]
        The CIK of the company if no symbol is provided.
    period : Literal["annual", "quarter"]
        The period of the income statement. Default is "annual".
    limit : Optional[NonNegativeInt]
        The limit of the income statement.
    """

    symbol: Optional[str]
    cik: Optional[str]
    period: PeriodType = Field(default="annual")
    limit: Optional[NonNegativeInt]

    @root_validator()
    def check_symbol_or_cik(cls, values):  # pylint: disable=no-self-argument
        if values.get("symbol") is None and values.get("cik") is None:
            raise ValueError("symbol or cik must be provided")
        return values


class FMPIncomeStatementData(Data):
    date: dateType
    symbol: str
    reportedCurrency: str = Field(alias="currency")
    cik: Optional[int]
    fillingDate: Optional[dateType] = Field(alias="filing_date")
    acceptedDate: Optional[datetime]
    calendarYear: Optional[int]
    period: Optional[str]
    revenue: Optional[int]
    costOfRevenue: Optional[int]
    grossProfit: Optional[int]
    grossProfitRatio: Optional[float]
    researchAndDevelopmentExpenses: Optional[int]
    generalAndAdministrativeExpenses: Optional[int]
    sellingAndMarketingExpenses: Optional[int]
    sellingGeneralAndAdministrativeExpenses: Optional[int]
    otherExpenses: Optional[int]
    operatingExpenses: Optional[int]
    costAndExpenses: Optional[int]
    interestIncome: Optional[int]
    interestExpense: Optional[int]
    depreciationAndAmortization: Optional[int]
    ebitda: Optional[int]
    ebitdaratio: Optional[float]
    operatingIncome: Optional[int]
    operatingIncomeRatio: Optional[float]
    totalOtherIncomeExpensesNet: Optional[int]
    incomeBeforeTax: Optional[int]
    incomeBeforeTaxRatio: Optional[float]
    incomeTaxExpense: Optional[int]
    netIncome: Optional[int]
    netIncomeRatio: Optional[float]
    eps: Optional[float]
    epsdiluted: Optional[float] = Field(alias="eps_diluted")
    weightedAverageShsOut: Optional[int] = Field(
        alias="weighted_average_shares_outstanding"
    )
    weightedAverageShsOutDil: Optional[int] = Field(
        alias="weighted_average_shares_outstanding_dil"
    )
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
        transformed_params = params
        transformed_params["period"] = (
            "annual" if params.get("period", "") == "annually" else "quarter"
        )
        return FMPIncomeStatementQueryParams(**transformed_params)

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
