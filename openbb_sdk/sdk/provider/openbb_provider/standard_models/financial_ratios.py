"""Financial ratios data model."""


from typing import List, Literal, Optional, Set, Union

from pydantic import Field, NonNegativeInt, validator

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.utils.descriptions import QUERY_DESCRIPTIONS


class FinancialRatiosQueryParams(QueryParams):
    """Financial Ratios Query."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))
    period: Literal["annual", "quarter"] = Field(
        default="annual", description=QUERY_DESCRIPTIONS.get("period", "")
    )
    limit: NonNegativeInt = Field(
        default=12, description=QUERY_DESCRIPTIONS.get("limit", "")
    )

    @validator("symbol", pre=True, check_fields=False, always=True)
    def upper_symbol(cls, v: Union[str, List[str], Set[str]]):
        """Convert symbol to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return ",".join([symbol.upper() for symbol in list(v)])


class FinancialRatiosData(Data):
    """Financial ratios data model."""

    symbol: str = Field(description="Symbol of the company.")
    date: str = Field(description="Date of the financial ratios.")
    period: str = Field(description="Period of the financial ratios.")
    current_ratio: Optional[float] = Field(description="Current ratio.")
    quick_ratio: Optional[float] = Field(description="Quick ratio.")
    cash_ratio: Optional[float] = Field(description="Cash ratio.")
    days_of_sales_outstanding: Optional[float] = Field(
        description="Days of sales outstanding."
    )
    days_of_inventory_outstanding: Optional[float] = Field(
        description="Days of inventory outstanding."
    )
    operating_cycle: Optional[float] = Field(description="Operating cycle.")
    days_of_payables_outstanding: Optional[float] = Field(
        description="Days of payables outstanding."
    )
    cash_conversion_cycle: Optional[float] = Field(description="Cash conversion cycle.")
    gross_profit_margin: Optional[float] = Field(description="Gross profit margin.")
    operating_profit_margin: Optional[float] = Field(
        description="Operating profit margin."
    )
    pretax_profit_margin: Optional[float] = Field(description="Pretax profit margin.")
    net_profit_margin: Optional[float] = Field(description="Net profit margin.")
    effective_tax_rate: Optional[float] = Field(description="Effective tax rate.")
    return_on_assets: Optional[float] = Field(description="Return on assets.")
    return_on_equity: Optional[float] = Field(description="Return on equity.")
    return_on_capital_employed: Optional[float] = Field(
        description="Return on capital employed."
    )
    net_income_per_ebt: Optional[float] = Field(description="Net income per EBT.")
    ebt_per_ebit: Optional[float] = Field(description="EBT per EBIT.")
    ebit_per_revenue: Optional[float] = Field(description="EBIT per revenue.")
    debt_ratio: Optional[float] = Field(description="Debt ratio.")
    debt_equity_ratio: Optional[float] = Field(description="Debt equity ratio.")
    long_term_debt_to_capitalization: Optional[float] = Field(
        description="Long term debt to capitalization."
    )
    total_debt_to_capitalization: Optional[float] = Field(
        description="Total debt to capitalization."
    )
    interest_coverage: Optional[float] = Field(description="Interest coverage.")
    cash_flow_to_debt_ratio: Optional[float] = Field(
        description="Cash flow to debt ratio."
    )
    company_equity_multiplier: Optional[float] = Field(
        description="Company equity multiplier."
    )
    receivables_turnover: Optional[float] = Field(description="Receivables turnover.")
    payables_turnover: Optional[float] = Field(description="Payables turnover.")
    inventory_turnover: Optional[float] = Field(description="Inventory turnover.")
    fixed_asset_turnover: Optional[float] = Field(description="Fixed asset turnover.")
    asset_turnover: Optional[float] = Field(description="Asset turnover.")
    operating_cash_flow_per_share: Optional[float] = Field(
        description="Operating cash flow per share."
    )
    free_cash_flow_per_share: Optional[float] = Field(
        description="Free cash flow per share."
    )
    cash_per_share: Optional[float] = Field(description="Cash per share.")
    payout_ratio: Optional[float] = Field(description="Payout ratio.")
    operating_cash_flow_sales_ratio: Optional[float] = Field(
        description="Operating cash flow sales ratio."
    )
    free_cash_flow_operating_cash_flow_ratio: Optional[float] = Field(
        description="Free cash flow operating cash flow ratio."
    )
    cash_flow_coverage_ratios: Optional[float] = Field(
        description="Cash flow coverage ratios."
    )
    short_term_coverage_ratios: Optional[float] = Field(
        description="Short term coverage ratios."
    )
    capital_expenditure_coverage_ratio: Optional[float] = Field(
        description="Capital expenditure coverage ratio."
    )
    dividend_paid_and_capex_coverage_ratio: Optional[float] = Field(
        description="Dividend paid and capex coverage ratio."
    )
    dividend_payout_ratio: Optional[float] = Field(description="Dividend payout ratio.")
    price_book_value_ratio: Optional[float] = Field(
        description="Price book value ratio."
    )
    price_to_book_ratio: Optional[float] = Field(description="Price to book ratio.")
    price_to_sales_ratio: Optional[float] = Field(description="Price to sales ratio.")
    price_earnings_ratio: Optional[float] = Field(description="Price earnings ratio.")
    price_to_free_cash_flows_ratio: Optional[float] = Field(
        description="Price to free cash flows ratio."
    )
    price_to_operating_cash_flows_ratio: Optional[float] = Field(
        description="Price to operating cash flows ratio."
    )
    price_cash_flow_ratio: Optional[float] = Field(description="Price cash flow ratio.")
    price_earnings_to_growth_ratio: Optional[float] = Field(
        description="Price earnings to growth ratio."
    )
    price_sales_ratio: Optional[float] = Field(description="Price sales ratio.")
    dividend_yield: Optional[float] = Field(description="Dividend yield.")
    enterprise_value_multiple: Optional[float] = Field(
        description="Enterprise value multiple."
    )
    price_fair_value: Optional[float] = Field(description="Price fair value.")
