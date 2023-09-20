"""Stock Multiples Data Model."""

from typing import List, Optional, Set, Union

from pydantic import Field, validator

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.utils.descriptions import QUERY_DESCRIPTIONS


class StockMultiplesQueryParams(QueryParams):
    """Stock Multiples Query."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))
    limit: Optional[int] = Field(
        default=100, description=QUERY_DESCRIPTIONS.get("limit", "")
    )

    @validator("symbol", pre=True, check_fields=False, always=True)
    def upper_symbol(cls, v: Union[str, List[str], Set[str]]):
        """Convert symbol to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return ",".join([symbol.upper() for symbol in list(v)])


class StockMultiplesData(Data):
    """Stock Multiples Data."""

    revenue_per_share_ttm: Optional[float] = Field(
        description="Revenue per share calculated as trailing twelve months."
    )
    net_income_per_share_ttm: Optional[float] = Field(
        description="Net income per share calculated as trailing twelve months."
    )
    operating_cash_flow_per_share_ttm: Optional[float] = Field(
        description="Operating cash flow per share calculated as trailing twelve months."
    )
    free_cash_flow_per_share_ttm: Optional[float] = Field(
        description="Free cash flow per share calculated as trailing twelve months."
    )
    cash_per_share_ttm: Optional[float] = Field(
        description="Cash per share calculated as trailing twelve months."
    )
    book_value_per_share_ttm: Optional[float] = Field(
        description="Book value per share calculated as trailing twelve months."
    )
    tangible_book_value_per_share_ttm: Optional[float] = Field(
        description="Tangible book value per share calculated as trailing twelve months."
    )
    shareholders_equity_per_share_ttm: Optional[float] = Field(
        description="Shareholders equity per share calculated as trailing twelve months."
    )
    interest_debt_per_share_ttm: Optional[float] = Field(
        description="Interest debt per share calculated as trailing twelve months."
    )
    market_cap_ttm: Optional[float] = Field(
        description="Market capitalization calculated as trailing twelve months."
    )
    enterprise_value_ttm: Optional[float] = Field(
        description="Enterprise value calculated as trailing twelve months."
    )
    pe_ratio_ttm: Optional[float] = Field(
        description="Price-to-earnings ratio (P/E ratio) calculated as trailing twelve months."
    )
    price_to_sales_ratio_ttm: Optional[float] = Field(
        description="Price-to-sales ratio calculated as trailing twelve months."
    )
    pocf_ratio_ttm: Optional[float] = Field(
        description="Price-to-operating cash flow ratio calculated as trailing twelve months."
    )
    pfcf_ratio_ttm: Optional[float] = Field(
        description="Price-to-free cash flow ratio calculated as trailing twelve months."
    )
    pb_ratio_ttm: Optional[float] = Field(
        description="Price-to-book ratio calculated as trailing twelve months."
    )
    ptb_ratio_ttm: Optional[float] = Field(
        description="Price-to-tangible book ratio calculated as trailing twelve months."
    )
    ev_to_sales_ttm: Optional[float] = Field(
        description="Enterprise value-to-sales ratio calculated as trailing twelve months."
    )
    enterprise_value_over_ebitda_ttm: Optional[float] = Field(
        description="Enterprise value-to-EBITDA ratio calculated as trailing twelve months."
    )
    ev_to_operating_cash_flow_ttm: Optional[float] = Field(
        description="Enterprise value-to-operating cash flow ratio calculated as trailing twelve months."
    )
    ev_to_free_cash_flow_ttm: Optional[float] = Field(
        description="Enterprise value-to-free cash flow ratio calculated as trailing twelve months."
    )
    earnings_yield_ttm: Optional[float] = Field(
        description="Earnings yield calculated as trailing twelve months."
    )
    free_cash_flow_yield_ttm: Optional[float] = Field(
        description="Free cash flow yield calculated as trailing twelve months."
    )
    debt_to_equity_ttm: Optional[float] = Field(
        description="Debt-to-equity ratio calculated as trailing twelve months."
    )
    debt_to_assets_ttm: Optional[float] = Field(
        description="Debt-to-assets ratio calculated as trailing twelve months."
    )
    net_debt_to_ebitda_ttm: Optional[float] = Field(
        description="Net debt-to-EBITDA ratio calculated as trailing twelve months."
    )
    current_ratio_ttm: Optional[float] = Field(
        description="Current ratio calculated as trailing twelve months."
    )
    interest_coverage_ttm: Optional[float] = Field(
        description="Interest coverage calculated as trailing twelve months."
    )
    income_quality_ttm: Optional[float] = Field(
        description="Income quality calculated as trailing twelve months."
    )
    dividend_yield_ttm: Optional[float] = Field(
        description="Dividend yield calculated as trailing twelve months."
    )
    dividend_yield_percentage_ttm: Optional[float] = Field(
        description="Dividend yield percentage calculated as trailing twelve months."
    )
    dividend_to_market_cap_ttm: Optional[float] = Field(
        description="Dividend to market capitalization ratio calculated as trailing twelve months."
    )
    dividend_per_share_ttm: Optional[float] = Field(
        description="Dividend per share calculated as trailing twelve months."
    )
    payout_ratio_ttm: Optional[float] = Field(
        description="Payout ratio calculated as trailing twelve months."
    )
    sales_general_and_administrative_to_revenue_ttm: Optional[float] = Field(
        description="Sales general and administrative expenses-to-revenue ratio calculated as trailing twelve months."
    )
    research_and_development_to_revenue_ttm: Optional[float] = Field(
        description="Research and development expenses-to-revenue ratio calculated as trailing twelve months."
    )
    intangibles_to_total_assets_ttm: Optional[float] = Field(
        description="Intangibles-to-total assets ratio calculated as trailing twelve months."
    )
    capex_to_operating_cash_flow_ttm: Optional[float] = Field(
        description="Capital expenditures-to-operating cash flow ratio calculated as trailing twelve months."
    )
    capex_to_revenue_ttm: Optional[float] = Field(
        description="Capital expenditures-to-revenue ratio calculated as trailing twelve months."
    )
    capex_to_depreciation_ttm: Optional[float] = Field(
        description="Capital expenditures-to-depreciation ratio calculated as trailing twelve months."
    )
    stock_based_compensation_to_revenue_ttm: Optional[float] = Field(
        description="Stock-based compensation-to-revenue ratio calculated as trailing twelve months."
    )
    graham_number_ttm: Optional[float] = Field(
        description="Graham number calculated as trailing twelve months."
    )
    roic_ttm: Optional[float] = Field(
        description="Return on invested capital calculated as trailing twelve months."
    )
    return_on_tangible_assets_ttm: Optional[float] = Field(
        description="Return on tangible assets calculated as trailing twelve months."
    )
    graham_net_net_ttm: Optional[float] = Field(
        description="Graham net-net working capital calculated as trailing twelve months."
    )
    working_capital_ttm: Optional[float] = Field(
        description="Working capital calculated as trailing twelve months."
    )
    tangible_asset_value_ttm: Optional[float] = Field(
        description="Tangible asset value calculated as trailing twelve months."
    )
    net_current_asset_value_ttm: Optional[float] = Field(
        description="Net current asset value calculated as trailing twelve months."
    )
    invested_capital_ttm: Optional[float] = Field(
        description="Invested capital calculated as trailing twelve months."
    )
    average_receivables_ttm: Optional[float] = Field(
        description="Average receivables calculated as trailing twelve months."
    )
    average_payables_ttm: Optional[float] = Field(
        description="Average payables calculated as trailing twelve months."
    )
    average_inventory_ttm: Optional[float] = Field(
        description="Average inventory calculated as trailing twelve months."
    )
    days_sales_outstanding_ttm: Optional[float] = Field(
        description="Days sales outstanding calculated as trailing twelve months."
    )
    days_payables_outstanding_ttm: Optional[float] = Field(
        description="Days payables outstanding calculated as trailing twelve months."
    )
    days_of_inventory_on_hand_ttm: Optional[float] = Field(
        description="Days of inventory on hand calculated as trailing twelve months."
    )
    receivables_turnover_ttm: Optional[float] = Field(
        description="Receivables turnover calculated as trailing twelve months."
    )
    payables_turnover_ttm: Optional[float] = Field(
        description="Payables turnover calculated as trailing twelve months."
    )
    inventory_turnover_ttm: Optional[float] = Field(
        description="Inventory turnover calculated as trailing twelve months."
    )
    roe_ttm: Optional[float] = Field(
        description="Return on equity calculated as trailing twelve months."
    )
    capex_per_share_ttm: Optional[float] = Field(
        description="Capital expenditures per share calculated as trailing twelve months."
    )
