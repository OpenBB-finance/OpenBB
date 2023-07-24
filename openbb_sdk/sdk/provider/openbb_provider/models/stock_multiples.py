"""Stock Multiples Data Model."""

from typing import Optional

from openbb_provider.abstract.data import Data, QueryParams
from openbb_provider.models.base import BaseSymbol


class StockMultiplesQueryParams(QueryParams, BaseSymbol):
    """Stock Multiples query model.

    Parameter
    ---------
    symbol : str
            The symbol of the company.
    limit : Optional[int]
            The limit of the key metrics ttm to be returned.
    """

    limit: Optional[int] = None


class StockMultiplesData(Data):
    """Stock Multiples Data.

    Returns
    -------
    revenue_per_share_ttm: Optional[float]
        The revenue per share of the stock calculated as trailing twelve months.
    net_income_per_share_ttm: Optional[float]
        The net income per share of the stock calculated as trailing twelve months.
    operating_cash_flow_per_share_ttm: Optional[float]
        The operating cash flow per share of the stock calculated as trailing twelve months.
    free_cash_flow_per_share_ttm: Optional[float]
        The free cash flow per share of the stock calculated as trailing twelve months.
    cash_per_share_ttm: Optional[float]
        The cash per share of the stock calculated as trailing twelve months.
    book_value_per_share_ttm: Optional[float]
        The book value per share of the stock calculated as trailing twelve months.
    tangible_book_value_per_share_ttm: Optional[float]
        The tangible book value per share of the stock calculated as trailing twelve months.
    shareholders_equity_per_share_ttm: Optional[float]
        The shareholders equity per share of the stock calculated as trailing twelve months.
    interest_debt_per_share_ttm: Optional[float]
        The interest debt per share of the stock calculated as trailing twelve months.
    market_cap_ttm: Optional[float]
        The market cap of the stock calculated as trailing twelve months.
    enterprise_value_ttm: Optional[float]
        The enterprise value of the stock calculated as trailing twelve months.
    pe_ratio_ttm: Optional[float]
        The PE ratio of the stock calculated as trailing twelve months.
    price_to_sales_ratio_ttm: Optional[float]
        The price to sales ratio of the stock calculated as trailing twelve months.
    pocf_ratio_ttm: Optional[float]
        The POCF ratio of the stock calculated as trailing twelve months.
    pfcf_ratio_ttm: Optional[float]
        The PFCF ratio of the stock calculated as trailing twelve months.
    pb_ratio_ttm: Optional[float]
        The PB ratio of the stock calculated as trailing twelve months.
    ptb_ratio_ttm: Optional[float]
        The PTB ratio of the stock calculated as trailing twelve months.
    ev_to_sales_ttm: Optional[float]
        The EV to sales of the stock calculated as trailing twelve months.
    enterprise_value_over_ebitda_ttm: Optional[float]
        The enterprise value over EBITDA of the stock calculated as trailing twelve months.
    ev_to_operating_cash_flow_ttm: Optional[float]
        The EV to operating cash flow of the stock calculated as trailing twelve months.
    ev_to_free_cash_flow_ttm: Optional[float]
        The EV to free cash flow of the stock calculated as trailing twelve months.
    earnings_yield_ttm: Optional[float]
        The earnings yield of the stock calculated as trailing twelve months.
    free_cash_flow_yield_ttm: Optional[float]
        The free cash flow yield of the stock calculated as trailing twelve months.
    debt_to_equity_ttm: Optional[float]
        The debt to equity of the stock calculated as trailing twelve months.
    debt_to_assets_ttm: Optional[float]
        The debt to assets of the stock calculated as trailing twelve months.
    net_debt_to_ebitda_ttm: Optional[float]
        The net debt to EBITDA of the stock calculated as trailing twelve months.
    current_ratio_ttm: Optional[float]
        The current ratio of the stock calculated as trailing twelve months.
    interest_coverage_ttm: Optional[float]
        The interest coverage of the stock calculated as trailing twelve months.
    income_quality_ttm: Optional[float]
        The income quality of the stock calculated as trailing twelve months.
    dividend_yield_ttm: Optional[float]
        The dividend yield of the stock calculated as trailing twelve months.
    payout_ratio_ttm: Optional[float]
        The payout ratio of the stock calculated as trailing twelve months.
    sales_general_and_administrative_to_revenue_ttm: Optional[float]
        The sales general and administrative to revenue of the stock calculated as trailing twelve months.
    research_and_development_to_revenue_ttm: Optional[float]
        The research and development to revenue of the stock calculated as trailing twelve months.
    intangibles_to_total_assets_ttm: Optional[float]
        The intangibles to total assets of the stock calculated as trailing twelve months.
    capex_to_operating_cash_flow_ttm: Optional[float]
        The capex to operating cash flow of the stock calculated as trailing twelve months.
    capex_to_revenue_ttm: Optional[float]
        The capex to revenue of the stock calculated as trailing twelve months.
    capex_to_depreciation_ttm: Optional[float]
        The capex to depreciation of the stock calculated as trailing twelve months.
    stock_based_compensation_to_revenue_ttm: Optional[float]
        The stock based compensation to revenue of the stock calculated as trailing twelve months.
    graham_number_ttm: Optional[float]
        The graham number of the stock calculated as trailing twelve months.
    roic_ttm: Optional[float]
        The ROIC of the stock calculated as trailing twelve months.
    return_on_tangible_assets_ttm: Optional[float]
        The return on tangible assets of the stock calculated as trailing twelve months.
    graham_net_net_ttm: Optional[float]
        The graham net net of the stock calculated as trailing twelve months.
    working_capital_ttm: Optional[float]
        The working capital of the stock calculated as trailing twelve months.
    tangible_asset_value_ttm: Optional[float]
        The tangible asset value of the stock calculated as trailing twelve months.
    net_current_asset_value_ttm: Optional[float]
        The net current asset value of the stock calculated as trailing twelve months.
    invested_capital_ttm: Optional[float]
        The invested capital of the stock calculated as trailing twelve months.
    average_receivables_ttm: Optional[float]
        The average receivables of the stock calculated as trailing twelve months.
    average_payables_ttm: Optional[float]
        The average payables of the stock calculated as trailing twelve months.
    average_inventory_ttm: Optional[float]
        The average inventory of the stock calculated as trailing twelve months.
    days_sales_outstanding_ttm: Optional[float]
        The days sales outstanding of the stock calculated as trailing twelve months.
    days_payables_outstanding_ttm: Optional[float]
        The days payables outstanding of the stock calculated as trailing twelve months.
    days_of_inventory_on_hand_ttm: Optional[float]
        The days of inventory on hand of the stock calculated as trailing twelve months.
    receivables_turnover_ttm: Optional[float]
        The receivables turnover of the stock calculated as trailing twelve months.
    payables_turnover_ttm: Optional[float]
        The payables turnover of the stock calculated as trailing twelve months.
    inventory_turnover_ttm: Optional[float]
        The inventory turnover of the stock calculated as trailing twelve months.
    roe_ttm: Optional[float]
        The ROE of the stock calculated as trailing twelve months.
    capex_per_share_ttm: Optional[float]
        The capex per share of the stock calculated as trailing twelve months.
    """

    revenue_per_share_ttm: Optional[float]
    net_income_per_share_ttm: Optional[float]
    operating_cash_flow_per_share_ttm: Optional[float]
    free_cash_flow_per_share_ttm: Optional[float]
    cash_per_share_ttm: Optional[float]
    book_value_per_share_ttm: Optional[float]
    tangible_book_value_per_share_ttm: Optional[float]
    shareholders_equity_per_share_ttm: Optional[float]
    interest_debt_per_share_ttm: Optional[float]
    market_cap_ttm: Optional[float]
    enterprise_value_ttm: Optional[float]
    pe_ratio_ttm: Optional[float]
    price_to_sales_ratio_ttm: Optional[float]
    pocf_ratio_ttm: Optional[float]
    pfcf_ratio_ttm: Optional[float]
    pb_ratio_ttm: Optional[float]
    ptb_ratio_ttm: Optional[float]
    ev_to_sales_ttm: Optional[float]
    enterprise_value_over_ebitda_ttm: Optional[float]
    ev_to_operating_cash_flow_ttm: Optional[float]
    ev_to_free_cash_flow_ttm: Optional[float]
    earnings_yield_ttm: Optional[float]
    free_cash_flow_yield_ttm: Optional[float]
    debt_to_equity_ttm: Optional[float]
    debt_to_assets_ttm: Optional[float]
    net_debt_to_ebitda_ttm: Optional[float]
    current_ratio_ttm: Optional[float]
    interest_coverage_ttm: Optional[float]
    income_quality_ttm: Optional[float]
    dividend_yield_ttm: Optional[float]
    payout_ratio_ttm: Optional[float]
    sales_general_and_administrative_to_revenue_ttm: Optional[float]
    research_and_development_to_revenue_ttm: Optional[float]
    intangibles_to_total_assets_ttm: Optional[float]
    capex_to_operating_cash_flow_ttm: Optional[float]
    capex_to_revenue_ttm: Optional[float]
    capex_to_depreciation_ttm: Optional[float]
    stock_based_compensation_to_revenue_ttm: Optional[float]
    graham_number_ttm: Optional[float]
    roic_ttm: Optional[float]
    return_on_tangible_assets_ttm: Optional[float]
    graham_net_net_ttm: Optional[float]
    working_capital_ttm: Optional[float]
    tangible_asset_value_ttm: Optional[float]
    net_current_asset_value_ttm: Optional[float]
    invested_capital_ttm: Optional[float]
    average_receivables_ttm: Optional[float]
    average_payables_ttm: Optional[float]
    average_inventory_ttm: Optional[float]
    days_sales_outstanding_ttm: Optional[float]
    days_payables_outstanding_ttm: Optional[float]
    days_of_inventory_on_hand_ttm: Optional[float]
    receivables_turnover_ttm: Optional[float]
    payables_turnover_ttm: Optional[float]
    inventory_turnover_ttm: Optional[float]
    roe_ttm: Optional[float]
    capex_per_share_ttm: Optional[float]
