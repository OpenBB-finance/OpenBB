"""Income Statement Growth Standard Model."""

import warnings
from datetime import date as dateType
from typing import List, Optional, Set, Union

from pydantic import Field, field_validator

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)

_warn = warnings.warn


class IncomeStatementGrowthQueryParams(QueryParams):
    """Income Statement Growth Query."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))
    period: str = Field(
        default="annual", description=QUERY_DESCRIPTIONS.get("period", "")
    )
    limit: int = Field(default=10, description=QUERY_DESCRIPTIONS.get("limit", ""))

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def upper_symbol(cls, v: str):
        """Convert symbol to uppercase."""
        if "," in v:
            _warn(
                f"{QUERY_DESCRIPTIONS.get('symbol_list_warning', '')} {v.split(',')[0].upper()}"
            )
        return v.split(",")[0].upper() if "," in v else v.upper()


class IncomeStatementGrowthData(Data):
    """Income Statement Growth Data. All values are normalized percent changes from the previous period."""

    symbol: Optional[str] = Field(
        default=None, description=DATA_DESCRIPTIONS.get("symbol", "")
    )
    period_ending: dateType = Field(description="Data for the fiscal period ending.")
    fiscal_year: Optional[int] = Field(
        default=None, description="Fiscal year of the fiscal period."
    )
    fiscal_period: Optional[str] = Field(
        default=None, description="Fiscal period of the fiscal year."
    )
    growth_revenue: Optional[float] = Field(
        default=None,
        description="Growth rate of total revenue.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    growth_cost_of_revenue: Optional[float] = Field(
        default=None,
        description="Growth rate of cost of goods sold.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    growth_gross_profit: Optional[float] = Field(
        default=None,
        description="Growth rate of gross profit.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    growth_gross_profit_ratio: Optional[float] = Field(
        default=None,
        description="Growth rate of gross profit as a percentage of revenue.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    growth_research_and_development_expenses: Optional[float] = Field(
        default=None,
        description="Growth rate of expenses on research and development.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    growth_general_and_administrative_expenses: Optional[float] = Field(
        default=None,
        description="Growth rate of general and administrative expenses.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    growth_selling_and_marketing_expenses: Optional[float] = Field(
        default=None,
        description="Growth rate of expenses on selling and marketing activities.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    growth_other_expenses: Optional[float] = Field(
        default=None,
        description="Growth rate of other operating expenses.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    growth_operating_expenses: Optional[float] = Field(
        default=None,
        description="Growth rate of total operating expenses.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    growth_cost_and_expenses: Optional[float] = Field(
        default=None,
        description="Growth rate of total costs and expenses.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    growth_interest_expense: Optional[float] = Field(
        default=None,
        description="Growth rate of interest expenses.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    growth_depreciation_and_amortization: Optional[float] = Field(
        default=None,
        description="Growth rate of depreciation and amortization expenses.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    growth_ebitda: Optional[float] = Field(
        default=None,
        description="Growth rate of Earnings Before Interest, Taxes, Depreciation, and Amortization.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    growth_ebitda_ratio: Optional[float] = Field(
        default=None,
        description="Growth rate of EBITDA as a percentage of revenue.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    growth_operating_income: Optional[float] = Field(
        default=None,
        description="Growth rate of operating income.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    growth_operating_income_ratio: Optional[float] = Field(
        default=None,
        description="Growth rate of operating income as a percentage of revenue.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    growth_total_other_income_expenses_net: Optional[float] = Field(
        default=None,
        description="Growth rate of net total other income and expenses.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    growth_income_before_tax: Optional[float] = Field(
        default=None,
        description="Growth rate of income before taxes.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    growth_income_before_tax_ratio: Optional[float] = Field(
        default=None,
        description="Growth rate of income before taxes as a percentage of revenue.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    growth_income_tax_expense: Optional[float] = Field(
        default=None,
        description="Growth rate of income tax expenses.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    growth_net_income: Optional[float] = Field(
        default=None,
        description="Growth rate of net income.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    growth_net_income_ratio: Optional[float] = Field(
        default=None,
        description="Growth rate of net income as a percentage of revenue.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    growth_eps: Optional[float] = Field(
        default=None,
        description="Growth rate of Earnings Per Share (EPS).",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    growth_eps_diluted: Optional[float] = Field(
        default=None,
        description="Growth rate of diluted Earnings Per Share (EPS).",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    growth_weighted_average_shares_outstanding: Optional[float] = Field(
        default=None,
        description="Growth rate of weighted average shares outstanding.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    growth_weighted_average_diluted_shares: Optional[float] = Field(
        default=None,
        description="Growth rate of diluted weighted average shares outstanding.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
