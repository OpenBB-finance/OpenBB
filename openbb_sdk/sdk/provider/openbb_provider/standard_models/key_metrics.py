"""Key Metrics Data Model."""


from datetime import date as dateType
from typing import List, Literal, Optional, Set, Union

from pydantic import Field, validator

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.utils.descriptions import DATA_DESCRIPTIONS, QUERY_DESCRIPTIONS


class KeyMetricsQueryParams(QueryParams):
    """Key Metrics Query."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))
    period: Literal["annual", "quarter"] = Field(
        default="annual", description=QUERY_DESCRIPTIONS.get("period", "")
    )
    limit: Optional[int] = Field(
        default=100, description=QUERY_DESCRIPTIONS.get("limit", "")
    )

    @validator("symbol", pre=True, check_fields=False, always=True)
    def upper_symbol(cls, v: Union[str, List[str], Set[str]]):
        """Convert symbol to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return ",".join([symbol.upper() for symbol in list(v)])


class KeyMetricsData(Data):
    """Key Metrics Data."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))
    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    period: str = Field(description="Period of the data.")
    revenue_per_share: Optional[float] = Field(description="Revenue per share")
    net_income_per_share: Optional[float] = Field(description="Net income per share")
    operating_cash_flow_per_share: Optional[float] = Field(
        description="Operating cash flow per share"
    )
    free_cash_flow_per_share: Optional[float] = Field(
        description="Free cash flow per share"
    )
    cash_per_share: Optional[float] = Field(description="Cash per share")
    book_value_per_share: Optional[float] = Field(description="Book value per share")
    tangible_book_value_per_share: Optional[float] = Field(
        description="Tangible book value per share"
    )
    shareholders_equity_per_share: Optional[float] = Field(
        description="Shareholders equity per share"
    )
    interest_debt_per_share: Optional[float] = Field(
        description="Interest debt per share"
    )
    market_cap: Optional[float] = Field(description="Market capitalization")
    enterprise_value: Optional[float] = Field(description="Enterprise value")
    pe_ratio: Optional[float] = Field(description="Price-to-earnings ratio (P/E ratio)")
    price_to_sales_ratio: Optional[float] = Field(description="Price-to-sales ratio")
    pocf_ratio: Optional[float] = Field(
        description="Price-to-operating cash flow ratio"
    )
    pfcf_ratio: Optional[float] = Field(description="Price-to-free cash flow ratio")
    pb_ratio: Optional[float] = Field(description="Price-to-book ratio")
    ptb_ratio: Optional[float] = Field(description="Price-to-tangible book ratio")
    ev_to_sales: Optional[float] = Field(description="Enterprise value-to-sales ratio")
    enterprise_value_over_ebitda: Optional[float] = Field(
        description="Enterprise value-to-EBITDA ratio"
    )
    ev_to_operating_cash_flow: Optional[float] = Field(
        description="Enterprise value-to-operating cash flow ratio"
    )
    ev_to_free_cash_flow: Optional[float] = Field(
        description="Enterprise value-to-free cash flow ratio"
    )
    earnings_yield: Optional[float] = Field(description="Earnings yield")
    free_cash_flow_yield: Optional[float] = Field(description="Free cash flow yield")
    debt_to_equity: Optional[float] = Field(description="Debt-to-equity ratio")
    debt_to_assets: Optional[float] = Field(description="Debt-to-assets ratio")
    net_debt_to_ebitda: Optional[float] = Field(description="Net debt-to-EBITDA ratio")
    current_ratio: Optional[float] = Field(description="Current ratio")
    interest_coverage: Optional[float] = Field(description="Interest coverage")
    income_quality: Optional[float] = Field(description="Income quality")
    dividend_yield: Optional[float] = Field(description="Dividend yield")
    payout_ratio: Optional[float] = Field(description="Payout ratio")
    sales_general_and_administrative_to_revenue: Optional[float] = Field(
        description="Sales general and administrative expenses-to-revenue ratio"
    )
    research_and_development_to_revenue: Optional[float] = Field(
        description="Research and development expenses-to-revenue ratio"
    )
    intangibles_to_total_assets: Optional[float] = Field(
        description="Intangibles-to-total assets ratio"
    )
    capex_to_operating_cash_flow: Optional[float] = Field(
        description="Capital expenditures-to-operating cash flow ratio"
    )
    capex_to_revenue: Optional[float] = Field(
        description="Capital expenditures-to-revenue ratio"
    )
    capex_to_depreciation: Optional[float] = Field(
        description="Capital expenditures-to-depreciation ratio"
    )
    stock_based_compensation_to_revenue: Optional[float] = Field(
        description="Stock-based compensation-to-revenue ratio"
    )
    graham_number: Optional[float] = Field(description="Graham number")
    roic: Optional[float] = Field(description="Return on invested capital")
    return_on_tangible_assets: Optional[float] = Field(
        description="Return on tangible assets"
    )
    graham_net_net: Optional[float] = Field(
        description="Graham net-net working capital"
    )
    working_capital: Optional[float] = Field(description="Working capital")
    tangible_asset_value: Optional[float] = Field(description="Tangible asset value")
    net_current_asset_value: Optional[float] = Field(
        description="Net current asset value"
    )
    invested_capital: Optional[float] = Field(description="Invested capital")
    average_receivables: Optional[float] = Field(description="Average receivables")
    average_payables: Optional[float] = Field(description="Average payables")
    average_inventory: Optional[float] = Field(description="Average inventory")
    days_sales_outstanding: Optional[float] = Field(
        description="Days sales outstanding"
    )
    days_payables_outstanding: Optional[float] = Field(
        description="Days payables outstanding"
    )
    days_of_inventory_on_hand: Optional[float] = Field(
        description="Days of inventory on hand"
    )
    receivables_turnover: Optional[float] = Field(description="Receivables turnover")
    payables_turnover: Optional[float] = Field(description="Payables turnover")
    inventory_turnover: Optional[float] = Field(description="Inventory turnover")
    roe: Optional[float] = Field(description="Return on equity")
    capex_per_share: Optional[float] = Field(
        description="Capital expenditures per share"
    )

    @validator("symbol", pre=True, check_fields=False, always=True)
    def upper_symbol(cls, v: Union[str, List[str], Set[str]]):
        """Convert symbol to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return ",".join([symbol.upper() for symbol in list(v)])
