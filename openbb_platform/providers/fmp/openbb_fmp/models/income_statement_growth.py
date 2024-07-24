"""FMP Income Statement Growth Model."""

from typing import Any, Dict, List, Literal, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.income_statement_growth import (
    IncomeStatementGrowthData,
    IncomeStatementGrowthQueryParams,
)
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from openbb_fmp.utils.helpers import create_url, get_data_many
from pydantic import Field, model_validator


class FMPIncomeStatementGrowthQueryParams(IncomeStatementGrowthQueryParams):
    """FMP Income Statement Growth Query.

    Source: https://site.financialmodelingprep.com/developer/docs/financial-statements-growth-api/
    """

    __json_schema_extra__ = {
        "period": {
            "choices": ["annual", "quarter"],
        }
    }

    period: Literal["annual", "quarter"] = Field(
        default="annual",
        description=QUERY_DESCRIPTIONS.get("period", ""),
    )


class FMPIncomeStatementGrowthData(IncomeStatementGrowthData):
    """FMP Income Statement Growth Data."""

    __alias_dict__ = {
        "period_ending": "date",
        "fiscal_year": "calendarYear",
        "fiscal_period": "period",
        "growth_ebitda": "growthEBITDA",
        "growth_ebitda_ratio": "growthEBITDARatio",
        "growth_basic_earings_per_share": "growthEPS",
        "growth_net_income_margin": "growthNetIncomeRatio",
        "growth_consolidated_net_income": "growthNetIncome",
        "growth_gross_profit_margin": "growthGrossProfitRatio",
        "growth_income_before_tax_margin": "growthIncomeBeforeTaxRatio",
        "growth_operating_income_margin": "growthOperatingIncomeRatio",
        "growth_diluted_earnings_per_share": "growthEPSDiluted",
        "growth_weighted_average_basic_shares_outstanding": "growthWeightedAverageShsOut",
        "growth_weighted_average_diluted_shares_outstanding": "growthWeightedAverageShsOutDil",
        "growth_research_and_development_expense": "growthResearchAndDevelopmentExpenses",
        "growth_general_and_admin_expense": "growthGeneralAndAdministrativeExpenses",
        "growth_selling_and_marketing_expense": "growthSellingAndMarketingExpenses",
    }

    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    growth_revenue: Optional[float] = Field(
        default=None,
        description="Growth rate of total revenue.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_cost_of_revenue: Optional[float] = Field(
        default=None,
        description="Growth rate of cost of goods sold.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_gross_profit: Optional[float] = Field(
        default=None,
        description="Growth rate of gross profit.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_gross_profit_margin: Optional[float] = Field(
        default=None,
        description="Growth rate of gross profit as a percentage of revenue.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_general_and_admin_expense: Optional[float] = Field(
        default=None,
        description="Growth rate of general and administrative expenses.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_research_and_development_expense: Optional[float] = Field(
        default=None,
        description="Growth rate of expenses on research and development.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_selling_and_marketing_expense: Optional[float] = Field(
        default=None,
        description="Growth rate of expenses on selling and marketing activities.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_other_expenses: Optional[float] = Field(
        default=None,
        description="Growth rate of other operating expenses.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_operating_expenses: Optional[float] = Field(
        default=None,
        description="Growth rate of total operating expenses.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_cost_and_expenses: Optional[float] = Field(
        default=None,
        description="Growth rate of total costs and expenses.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_interest_expense: Optional[float] = Field(
        default=None,
        description="Growth rate of interest expenses.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_depreciation_and_amortization: Optional[float] = Field(
        default=None,
        description="Growth rate of depreciation and amortization expenses.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_ebitda: Optional[float] = Field(
        default=None,
        description="Growth rate of Earnings Before Interest, Taxes, Depreciation, and Amortization.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_ebitda_margin: Optional[float] = Field(
        default=None,
        description="Growth rate of EBITDA as a percentage of revenue.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_operating_income: Optional[float] = Field(
        default=None,
        description="Growth rate of operating income.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_operating_income_margin: Optional[float] = Field(
        default=None,
        description="Growth rate of operating income as a percentage of revenue.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_total_other_income_expenses_net: Optional[float] = Field(
        default=None,
        description="Growth rate of net total other income and expenses.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_income_before_tax: Optional[float] = Field(
        default=None,
        description="Growth rate of income before taxes.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_income_before_tax_margin: Optional[float] = Field(
        default=None,
        description="Growth rate of income before taxes as a percentage of revenue.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_income_tax_expense: Optional[float] = Field(
        default=None,
        description="Growth rate of income tax expenses.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_consolidated_net_income: Optional[float] = Field(
        default=None,
        description="Growth rate of net income.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_net_income_margin: Optional[float] = Field(
        default=None,
        description="Growth rate of net income as a percentage of revenue.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_basic_earings_per_share: Optional[float] = Field(
        default=None,
        description="Growth rate of Earnings Per Share (EPS).",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_diluted_earnings_per_share: Optional[float] = Field(
        default=None,
        description="Growth rate of diluted Earnings Per Share (EPS).",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_weighted_average_basic_shares_outstanding: Optional[float] = Field(
        default=None,
        description="Growth rate of weighted average shares outstanding.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_weighted_average_diluted_shares_outstanding: Optional[float] = Field(
        default=None,
        description="Growth rate of diluted weighted average shares outstanding.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )

    @model_validator(mode="before")
    @classmethod
    def replace_zero(cls, values):
        """Check for zero values and replace with None."""
        return (
            {k: None if v == 0 else v for k, v in values.items()}
            if isinstance(values, dict)
            else values
        )


class FMPIncomeStatementGrowthFetcher(
    Fetcher[
        FMPIncomeStatementGrowthQueryParams,
        List[FMPIncomeStatementGrowthData],
    ]
):
    """FMP Income Statement Growth Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPIncomeStatementGrowthQueryParams:
        """Transform the query params."""
        return FMPIncomeStatementGrowthQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FMPIncomeStatementGrowthQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""

        url = create_url(
            3, f"income-statement-growth/{query.symbol}", api_key, query, ["symbol"]
        )

        return await get_data_many(url, **kwargs)

    @staticmethod
    def transform_data(
        query: FMPIncomeStatementGrowthQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[FMPIncomeStatementGrowthData]:
        """Return the transformed data."""
        return [FMPIncomeStatementGrowthData.model_validate(d) for d in data]
