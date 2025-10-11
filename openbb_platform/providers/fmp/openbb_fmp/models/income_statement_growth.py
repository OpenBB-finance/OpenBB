"""FMP Income Statement Growth Model."""

# pylint: disable=unused-argument

from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.income_statement_growth import (
    IncomeStatementGrowthData,
    IncomeStatementGrowthQueryParams,
)
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from openbb_fmp.utils.definitions import FinancialPeriods
from pydantic import Field


class FMPIncomeStatementGrowthQueryParams(IncomeStatementGrowthQueryParams):
    """FMP Income Statement Growth Query.

    Source: https://site.financialmodelingprep.com/developer/docs#income-statement-growth
    """

    period: FinancialPeriods = Field(
        default="annual",
        description=QUERY_DESCRIPTIONS.get("period", ""),
    )


class FMPIncomeStatementGrowthData(IncomeStatementGrowthData):
    """FMP Income Statement Growth Data."""

    __alias_dict__ = {
        "period_ending": "date",
        "fiscal_year": "calendarYear",
        "fiscal_period": "period",
        "growth_ebit": "growthEBIT",
        "growth_ebitda": "growthEBITDA",
        "growth_basic_earings_per_share": "growthEPS",
        "growth_gross_profit_margin": "growthGrossProfitRatio",
        "growth_consolidated_net_income": "growthNetIncome",
        "growth_diluted_earnings_per_share": "growthEPSDiluted",
        "growth_weighted_average_basic_shares_outstanding": "growthWeightedAverageShsOut",
        "growth_weighted_average_diluted_shares_outstanding": "growthWeightedAverageShsOutDil",
        "growth_research_and_development_expense": "growthResearchAndDevelopmentExpenses",
        "growth_general_and_admin_expense": "growthGeneralAndAdministrativeExpenses",
        "growth_selling_and_marketing_expense": "growthSellingAndMarketingExpenses",
    }

    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    reported_currency: str | None = Field(
        description="The currency in which the financial data is reported.",
        default=None,
    )
    growth_revenue: float | None = Field(
        default=None,
        description="Growth rate of total revenue.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_cost_of_revenue: float | None = Field(
        default=None,
        description="Growth rate of cost of goods sold.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_gross_profit: float | None = Field(
        default=None,
        description="Growth rate of gross profit.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_gross_profit_margin: float | None = Field(
        default=None,
        description="Growth rate of gross profit as a percentage of revenue.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_general_and_admin_expense: float | None = Field(
        default=None,
        description="Growth rate of general and administrative expenses.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_research_and_development_expense: float | None = Field(
        default=None,
        description="Growth rate of expenses on research and development.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_selling_and_marketing_expense: float | None = Field(
        default=None,
        description="Growth rate of expenses on selling and marketing activities.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_other_expenses: float | None = Field(
        default=None,
        description="Growth rate of other operating expenses.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_operating_expenses: float | None = Field(
        default=None,
        description="Growth rate of total operating expenses.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_cost_and_expenses: float | None = Field(
        default=None,
        description="Growth rate of total costs and expenses.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_depreciation_and_amortization: float | None = Field(
        default=None,
        description="Growth rate of depreciation and amortization expenses.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_interest_income: float | None = Field(
        default=None,
        description="Growth rate of interest income.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_interest_expense: float | None = Field(
        default=None,
        description="Growth rate of interest expenses.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_net_interest_income: float | None = Field(
        default=None,
        description="Growth rate of net interest income.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_ebit: float | None = Field(
        default=None,
        description="Growth rate of Earnings Before Interest and Taxes (EBIT).",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_ebitda: float | None = Field(
        default=None,
        description="Growth rate of Earnings Before Interest, Taxes, Depreciation, and Amortization.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_operating_income: float | None = Field(
        default=None,
        description="Growth rate of operating income.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_non_operating_income_excluding_interest: float | None = Field(
        default=None,
        description="Growth rate of non-operating income excluding interest.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_total_other_income_expenses_net: float | None = Field(
        default=None,
        description="Growth rate of net total other income and expenses.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_other_adjustments_to_net_income: float | None = Field(
        default=None,
        description="Growth rate of other adjustments to net income.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_net_income_deductions: float | None = Field(
        default=None,
        description="Growth rate of net income deductions.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_income_before_tax: float | None = Field(
        default=None,
        description="Growth rate of income before taxes.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_income_tax_expense: float | None = Field(
        default=None,
        description="Growth rate of income tax expenses.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_net_income_from_continuing_operations: float | None = Field(
        default=None,
        description="Growth rate of net income from continuing operations.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_consolidated_net_income: float | None = Field(
        default=None,
        description="Growth rate of net income.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_basic_earings_per_share: float | None = Field(
        default=None,
        description="Growth rate of Earnings Per Share (EPS).",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_diluted_earnings_per_share: float | None = Field(
        default=None,
        description="Growth rate of diluted Earnings Per Share (EPS).",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_weighted_average_basic_shares_outstanding: float | None = Field(
        default=None,
        description="Growth rate of weighted average shares outstanding.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_weighted_average_diluted_shares_outstanding: float | None = Field(
        default=None,
        description="Growth rate of diluted weighted average shares outstanding.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )


class FMPIncomeStatementGrowthFetcher(
    Fetcher[
        FMPIncomeStatementGrowthQueryParams,
        list[FMPIncomeStatementGrowthData],
    ]
):
    """FMP Income Statement Growth Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> FMPIncomeStatementGrowthQueryParams:
        """Transform the query params."""
        return FMPIncomeStatementGrowthQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FMPIncomeStatementGrowthQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the FMP endpoint."""
        # pylint: disable=import-outside-toplevel
        from openbb_fmp.utils.helpers import get_data_many

        api_key = credentials.get("fmp_api_key") if credentials else ""

        url = (
            "https://financialmodelingprep.com/stable/income-statement-growth"
            + f"?symbol={query.symbol}"
            + f"&period={query.period}"
            + f"&limit={query.limit if query.limit else 5}"
            + f"&apikey={api_key}"
        )

        return await get_data_many(url, **kwargs)

    @staticmethod
    def transform_data(
        query: FMPIncomeStatementGrowthQueryParams, data: list[dict], **kwargs: Any
    ) -> list[FMPIncomeStatementGrowthData]:
        """Return the transformed data."""
        return [FMPIncomeStatementGrowthData.model_validate(d) for d in data]
