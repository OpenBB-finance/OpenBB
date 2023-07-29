"""Key Metrics Data Model."""


from datetime import date as DateType
from typing import Literal, Optional

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.models.base import BaseSymbol


class KeyMetricsQueryParams(QueryParams, BaseSymbol):
    """Key Metrics query model.

    Parameter
    ---------
    symbol : str
        The symbol of the company.
    """

    period: Literal["annually", "quarterly"] = "annually"
    limit: Optional[int] = None


class KeyMetricsData(Data):
    """Return Key Metrics Data.

    Returns
    -------
    symbol : str
        The symbol of the stock.
    date : DateType
        The date of the key metrics.
    period : str
        The period of the key metrics.
    revenue_per_share : float
        The revenue per share of the stock.
    net_income_per_share : float
        The net income per share of the stock.
    operating_cash_flow_per_share : float
        The operating cash flow per share of the stock.
    free_cash_flow_per_share : float
        The free cash flow per share of the stock.
    cash_per_share : float
        The cash per share of the stock.
    book_value_per_share : float
        The book value per share of the stock.
    tangible_book_value_per_share : float
        The tangible book value per share of the stock.
    shareholders_equity_per_share : float
        The shareholders equity per share of the stock.
    interest_debt_per_share : float
        The interest debt per share of the stock.
    market_cap : float
        The market cap of the stock.
    enterprise_value : float
        The enterprise value of the stock.
    pe_ratio : float
        The PE ratio of the stock.
    price_to_sales_ratio : float
        The price to sales ratio of the stock.
    pocf_ratio : float
        The POCF ratio of the stock.
    pfcf_ratio : float
        The PFCF ratio of the stock.
    pb_ratio : float
        The PB ratio of the stock.
    ptb_ratio : float
        The PTB ratio of the stock.
    ev_to_sales : float
        The EV to sales of the stock.
    enterprise_value_over_ebitda : float
        The enterprise value over EBITDA of the stock.
    ev_to_operating_cash_flow : float
        The EV to operating cash flow of the stock.
    ev_to_free_cash_flow : float
        The EV to free cash flow of the stock.
    earnings_yield : float
        The earnings yield of the stock.
    free_cash_flow_yield : float
        The free cash flow yield of the stock.
    debt_to_equity : float
        The debt to equity of the stock.
    debt_to_assets : float
        The debt to assets of the stock.
    net_debt_to_ebitda : float
        The net debt to EBITDA of the stock.
    current_ratio : float
        The current ratio of the stock.
    interest_coverage : float
        The interest coverage of the stock.
    income_quality : float
        The income quality of the stock.
    dividend_yield : float
        The dividend yield of the stock.
    payout_ratio : float
        The payout ratio of the stock.
    sales_general_and_administrative_to_revenue : float
        The sales general and administrative to revenue of the stock.
    research_and_developement_to_revenue : float
        The research and development to revenue of the stock.
    intangibles_to_total_assets : float
        The intangibles to total assets of the stock.
    capex_to_operating_cash_flow : float
        The capex to operating cash flow of the stock.
    capex_to_revenue : float
        The capex to revenue of the stock.
    capex_to_depreciation : float
        The capex to depreciation of the stock.
    stock_based_compensation_to_revenue : float
        The stock based compensation to revenue of the stock.
    graham_number : float
        The graham number of the stock.
    roic : float
        The ROIC of the stock.
    return_on_tangible_assets : float
        The return on tangible assets of the stock.
    graham_net_net : float
        The graham net net of the stock.
    working_capital : float
        The working capital of the stock.
    tangible_asset_value : float
        The tangible asset value of the stock.
    net_current_asset_value : float
        The net current asset value of the stock.
    invested_capital : float
        The invested capital of the stock.
    average_receivables : float
        The average receivables of the stock.
    average_payables : float
        The average payables of the stock.
    average_inventory : float
        The average inventory of the stock.
    days_sales_outstanding : float
        The days sales outstanding of the stock.
    days_payables_outstanding : float
        The days payables outstanding of the stock.
    days_of_inventory_on_hand : float
        The days of inventory on hand of the stock.
    receivables_turnover : float
        The receivables turnover of the stock.
    payables_turnover : float
        The payables turnover of the stock.
    inventory_turnover : float
        The inventory turnover of the stock.
    roe : float
        The ROE of the stock.
    capex_per_share : float
        The capex per share of the stock.
    """

    symbol: str
    date: DateType
    period: str
    revenue_per_share: Optional[float]
    net_income_per_share: Optional[float]
    operating_cash_flow_per_share: Optional[float]
    free_cash_flow_per_share: Optional[float]
    cash_per_share: Optional[float]
    book_value_per_share: Optional[float]
    tangible_book_value_per_share: Optional[float]
    shareholders_equity_per_share: Optional[float]
    interest_debt_per_share: Optional[float]
    market_cap: Optional[float]
    enterprise_value: Optional[float]
    pe_ratio: Optional[float]
    price_to_sales_ratio: Optional[float]
    pocf_ratio: Optional[float]
    pfcf_ratio: Optional[float]
    pb_ratio: Optional[float]
    ptb_ratio: Optional[float]
    ev_to_sales: Optional[float]
    enterprise_value_over_ebitda: Optional[float]
    ev_to_operating_cash_flow: Optional[float]
    ev_to_free_cash_flow: Optional[float]
    earnings_yield: Optional[float]
    free_cash_flow_yield: Optional[float]
    debt_to_equity: Optional[float]
    debt_to_assets: Optional[float]
    net_debt_to_ebitda: Optional[float]
    current_ratio: Optional[float]
    interest_coverage: Optional[float]
    income_quality: Optional[float]
    dividend_yield: Optional[float]
    payout_ratio: Optional[float]
    sales_general_and_administrative_to_revenue: Optional[float]
    research_and_development_to_revenue: Optional[float]
    intangibles_to_total_assets: Optional[float]
    capex_to_operating_cash_flow: Optional[float]
    capex_to_revenue: Optional[float]
    capex_to_depreciation: Optional[float]
    stock_based_compensation_to_revenue: Optional[float]
    graham_number: Optional[float]
    roic: Optional[float]
    return_on_tangible_assets: Optional[float]
    graham_net_net: Optional[float]
    working_capital: Optional[float]
    tangible_asset_value: Optional[float]
    net_current_asset_value: Optional[float]
    invested_capital: Optional[float]
    average_receivables: Optional[float]
    average_payables: Optional[float]
    average_inventory: Optional[float]
    days_sales_outstanding: Optional[float]
    days_payables_outstanding: Optional[float]
    days_of_inventory_on_hand: Optional[float]
    receivables_turnover: Optional[float]
    payables_turnover: Optional[float]
    inventory_turnover: Optional[float]
    roe: Optional[float]
    capex_per_share: Optional[float]
