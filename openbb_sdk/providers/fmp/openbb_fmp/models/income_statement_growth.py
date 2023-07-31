"""FMP Income Statement Growth Fetcher."""


from datetime import datetime
from typing import Any, Dict, List, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.models.income_statement_growth import (
    IncomeStatementGrowthData,
    IncomeStatementGrowthQueryParams,
)
from openbb_fmp.utils.helpers import create_url, get_data_many

from pydantic import validator


class FMPIncomeStatementGrowthQueryParams(IncomeStatementGrowthQueryParams):
    """FMP Income Statement Growth QueryParams.

    Source: https://site.financialmodelingprep.com/developer/docs/financial-statements-growth-api/
    """


class FMPIncomeStatementGrowthData(IncomeStatementGrowthData):
    """FMP Income Statement Growth Data."""

    class Config:
        fields = {
            "growth_revenue": "growthRevenue",
            "growth_cost_of_revenue": "growthCostOfRevenue",
            "growth_gross_profit": "growthGrossProfit",
            "growth_gross_profit_ratio": "growthGrossProfitRatio",
            "growth_research_and_development_expenses": "growthResearchAndDevelopmentExpenses",
            "growth_general_and_administrative_expenses": "growthGeneralAndAdministrativeExpenses",
            "growth_selling_and_marketing_expenses": "growthSellingAndMarketingExpenses",
            "growth_other_expenses": "growthOtherExpenses",
            "growth_operating_expenses": "growthOperatingExpenses",
            "growth_cost_and_expenses": "growthCostAndExpenses",
            "growth_interest_expense": "growthInterestExpense",
            "growth_depreciation_and_amortization": "growthDepreciationAndAmortization",
            "growth_ebitda": "growthEBITDA",
            "growth_ebitda_ratio": "growthEBITDARatio",
            "growth_operating_income": "growthOperatingIncome",
            "growth_operating_income_ratio": "growthOperatingIncomeRatio",
            "growth_total_other_income_expenses_net": "growthTotalOtherIncomeExpensesNet",
            "growth_income_before_tax": "growthIncomeBeforeTax",
            "growth_income_before_tax_ratio": "growthIncomeBeforeTaxRatio",
            "growth_income_tax_expense": "growthIncomeTaxExpense",
            "growth_net_income": "growthNetIncome",
            "growth_net_income_ratio": "growthNetIncomeRatio",
            "growth_eps": "growthEPS",
            "growth_eps_diluted": "growthEPSDiluted",
            "growth_weighted_average_shs_out": "growthWeightedAverageShsOut",
            "growth_weighted_average_shs_out_dil": "growthWeightedAverageShsOutDil",
        }

    @validator("date", pre=True, check_fields=False)
    def date_validate(cls, v):  # pylint: disable=E0213
        return datetime.strptime(v, "%Y-%m-%d")


class FMPIncomeStatementGrowthFetcher(
    Fetcher[
        IncomeStatementGrowthQueryParams,
        IncomeStatementGrowthData,
        FMPIncomeStatementGrowthQueryParams,
        FMPIncomeStatementGrowthData,
    ]
):
    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPIncomeStatementGrowthQueryParams:
        return FMPIncomeStatementGrowthQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FMPIncomeStatementGrowthQueryParams,
        credentials: Optional[Dict[str, str]],
    ) -> List[FMPIncomeStatementGrowthData]:
        api_key = credentials.get("fmp_api_key") if credentials else ""

        query.period = "annual" if query.period == "annually" else "quarter"

        url = create_url(
            3, f"income-statement-growth/{query.symbol}", api_key, query, ["symbol"]
        )
        return get_data_many(url, FMPIncomeStatementGrowthData)

    @staticmethod
    def transform_data(
        data: List[FMPIncomeStatementGrowthData],
    ) -> List[FMPIncomeStatementGrowthData]:
        return data
