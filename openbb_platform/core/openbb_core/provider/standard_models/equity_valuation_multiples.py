"""Equity Valuation Multiples Standard Model."""

from typing import Optional

from pydantic import Field, field_validator

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)


class EquityValuationMultiplesQueryParams(QueryParams):
    """Equity Valuation Multiples Query."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def to_upper(cls, v: str) -> str:
        """Convert field to uppercase."""
        return v.upper()


class EquityValuationMultiplesData(Data):
    """Equity Valuation Multiples Data."""

    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    revenue_per_share_ttm: Optional[float] = Field(
        default=None,
        description="Revenue per share calculated as trailing twelve months.",
    )
    net_income_per_share_ttm: Optional[float] = Field(
        default=None,
        description="Net income per share calculated as trailing twelve months.",
    )
    operating_cash_flow_per_share_ttm: Optional[float] = Field(
        default=None,
        description="Operating cash flow per share calculated as trailing twelve months.",
    )
    free_cash_flow_per_share_ttm: Optional[float] = Field(
        default=None,
        description="Free cash flow per share calculated as trailing twelve months.",
    )
    cash_per_share_ttm: Optional[float] = Field(
        default=None, description="Cash per share calculated as trailing twelve months."
    )
    book_value_per_share_ttm: Optional[float] = Field(
        default=None,
        description="Book value per share calculated as trailing twelve months.",
    )
    tangible_book_value_per_share_ttm: Optional[float] = Field(
        default=None,
        description="Tangible book value per share calculated as trailing twelve months.",
    )
    shareholders_equity_per_share_ttm: Optional[float] = Field(
        default=None,
        description="Shareholders equity per share calculated as trailing twelve months.",
    )
    interest_debt_per_share_ttm: Optional[float] = Field(
        default=None,
        description="Interest debt per share calculated as trailing twelve months.",
    )
    market_cap_ttm: Optional[float] = Field(
        default=None,
        description="Market capitalization calculated as trailing twelve months.",
    )
    enterprise_value_ttm: Optional[float] = Field(
        default=None,
        description="Enterprise value calculated as trailing twelve months.",
    )
    pe_ratio_ttm: Optional[float] = Field(
        default=None,
        description="Price-to-earnings ratio (P/E ratio) calculated as trailing twelve months.",
    )
    price_to_sales_ratio_ttm: Optional[float] = Field(
        default=None,
        description="Price-to-sales ratio calculated as trailing twelve months.",
    )
    pocf_ratio_ttm: Optional[float] = Field(
        default=None,
        description="Price-to-operating cash flow ratio calculated as trailing twelve months.",
    )
    pfcf_ratio_ttm: Optional[float] = Field(
        default=None,
        description="Price-to-free cash flow ratio calculated as trailing twelve months.",
    )
    pb_ratio_ttm: Optional[float] = Field(
        default=None,
        description="Price-to-book ratio calculated as trailing twelve months.",
    )
    ptb_ratio_ttm: Optional[float] = Field(
        default=None,
        description="Price-to-tangible book ratio calculated as trailing twelve months.",
    )
    ev_to_sales_ttm: Optional[float] = Field(
        default=None,
        description="Enterprise value-to-sales ratio calculated as trailing twelve months.",
    )
    enterprise_value_over_ebitda_ttm: Optional[float] = Field(
        default=None,
        description="Enterprise value-to-EBITDA ratio calculated as trailing twelve months.",
    )
    ev_to_operating_cash_flow_ttm: Optional[float] = Field(
        default=None,
        description="Enterprise value-to-operating cash flow ratio calculated as trailing twelve months.",
    )
    ev_to_free_cash_flow_ttm: Optional[float] = Field(
        default=None,
        description="Enterprise value-to-free cash flow ratio calculated as trailing twelve months.",
    )
    earnings_yield_ttm: Optional[float] = Field(
        default=None, description="Earnings yield calculated as trailing twelve months."
    )
    free_cash_flow_yield_ttm: Optional[float] = Field(
        default=None,
        description="Free cash flow yield calculated as trailing twelve months.",
    )
    debt_to_equity_ttm: Optional[float] = Field(
        default=None,
        description="Debt-to-equity ratio calculated as trailing twelve months.",
    )
    debt_to_assets_ttm: Optional[float] = Field(
        default=None,
        description="Debt-to-assets ratio calculated as trailing twelve months.",
    )
    net_debt_to_ebitda_ttm: Optional[float] = Field(
        default=None,
        description="Net debt-to-EBITDA ratio calculated as trailing twelve months.",
    )
    current_ratio_ttm: Optional[float] = Field(
        default=None, description="Current ratio calculated as trailing twelve months."
    )
    interest_coverage_ttm: Optional[float] = Field(
        default=None,
        description="Interest coverage calculated as trailing twelve months.",
    )
    income_quality_ttm: Optional[float] = Field(
        default=None, description="Income quality calculated as trailing twelve months."
    )
    dividend_yield_ttm: Optional[float] = Field(
        default=None, description="Dividend yield calculated as trailing twelve months."
    )
    dividend_yield_percentage_ttm: Optional[float] = Field(
        default=None,
        description="Dividend yield percentage calculated as trailing twelve months.",
    )
    dividend_to_market_cap_ttm: Optional[float] = Field(
        default=None,
        description="Dividend to market capitalization ratio calculated as trailing twelve months.",
    )
    dividend_per_share_ttm: Optional[float] = Field(
        default=None,
        description="Dividend per share calculated as trailing twelve months.",
    )
    payout_ratio_ttm: Optional[float] = Field(
        default=None, description="Payout ratio calculated as trailing twelve months."
    )
    sales_general_and_administrative_to_revenue_ttm: Optional[float] = Field(
        default=None,
        description="Sales general and administrative expenses-to-revenue ratio calculated as trailing twelve months.",
    )
    research_and_development_to_revenue_ttm: Optional[float] = Field(
        default=None,
        description="Research and development expenses-to-revenue ratio calculated as trailing twelve months.",
    )
    intangibles_to_total_assets_ttm: Optional[float] = Field(
        default=None,
        description="Intangibles-to-total assets ratio calculated as trailing twelve months.",
    )
    capex_to_operating_cash_flow_ttm: Optional[float] = Field(
        default=None,
        description="Capital expenditures-to-operating cash flow ratio calculated as trailing twelve months.",
    )
    capex_to_revenue_ttm: Optional[float] = Field(
        default=None,
        description="Capital expenditures-to-revenue ratio calculated as trailing twelve months.",
    )
    capex_to_depreciation_ttm: Optional[float] = Field(
        default=None,
        description="Capital expenditures-to-depreciation ratio calculated as trailing twelve months.",
    )
    stock_based_compensation_to_revenue_ttm: Optional[float] = Field(
        default=None,
        description="Stock-based compensation-to-revenue ratio calculated as trailing twelve months.",
    )
    graham_number_ttm: Optional[float] = Field(
        default=None, description="Graham number calculated as trailing twelve months."
    )
    roic_ttm: Optional[float] = Field(
        default=None,
        description="Return on invested capital calculated as trailing twelve months.",
    )
    return_on_tangible_assets_ttm: Optional[float] = Field(
        default=None,
        description="Return on tangible assets calculated as trailing twelve months.",
    )
    graham_net_net_ttm: Optional[float] = Field(
        default=None,
        description="Graham net-net working capital calculated as trailing twelve months.",
    )
    working_capital_ttm: Optional[float] = Field(
        default=None,
        description="Working capital calculated as trailing twelve months.",
    )
    tangible_asset_value_ttm: Optional[float] = Field(
        default=None,
        description="Tangible asset value calculated as trailing twelve months.",
    )
    net_current_asset_value_ttm: Optional[float] = Field(
        default=None,
        description="Net current asset value calculated as trailing twelve months.",
    )
    invested_capital_ttm: Optional[float] = Field(
        default=None,
        description="Invested capital calculated as trailing twelve months.",
    )
    average_receivables_ttm: Optional[float] = Field(
        default=None,
        description="Average receivables calculated as trailing twelve months.",
    )
    average_payables_ttm: Optional[float] = Field(
        default=None,
        description="Average payables calculated as trailing twelve months.",
    )
    average_inventory_ttm: Optional[float] = Field(
        default=None,
        description="Average inventory calculated as trailing twelve months.",
    )
    days_sales_outstanding_ttm: Optional[float] = Field(
        default=None,
        description="Days sales outstanding calculated as trailing twelve months.",
    )
    days_payables_outstanding_ttm: Optional[float] = Field(
        default=None,
        description="Days payables outstanding calculated as trailing twelve months.",
    )
    days_of_inventory_on_hand_ttm: Optional[float] = Field(
        default=None,
        description="Days of inventory on hand calculated as trailing twelve months.",
    )
    receivables_turnover_ttm: Optional[float] = Field(
        default=None,
        description="Receivables turnover calculated as trailing twelve months.",
    )
    payables_turnover_ttm: Optional[float] = Field(
        default=None,
        description="Payables turnover calculated as trailing twelve months.",
    )
    inventory_turnover_ttm: Optional[float] = Field(
        default=None,
        description="Inventory turnover calculated as trailing twelve months.",
    )
    roe_ttm: Optional[float] = Field(
        default=None,
        description="Return on equity calculated as trailing twelve months.",
    )
    capex_per_share_ttm: Optional[float] = Field(
        default=None,
        description="Capital expenditures per share calculated as trailing twelve months.",
    )
