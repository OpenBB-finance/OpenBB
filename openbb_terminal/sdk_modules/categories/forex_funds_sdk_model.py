"""OpenBB Terminal SDK Forex Funds module."""
from datetime import datetime, timedelta
import logging

import openbb_terminal.sdk_init as lib
from openbb_terminal.sdk_modules.sdk_helpers import Category

logger = logging.getLogger(__name__)


def forex_quote(to_symbol: str = "USD", from_symbol: str = "EUR", source: str = "yf"):
    """Get the current quote for a given currency pair.

    Args:
        to_symbol (str, optional): The currency to convert to. Defaults to "USD".
        from_symbol (str, optional): The currency to convert from. Defaults to "EUR".
        source (str, optional): The source to get the quote from. Defaults to "yf".

    Returns:
        dict: A dictionary containing the quote information.
    """
    if source == "yf":
        return lib.forex_helpers.load(
            to_symbol,
            from_symbol,
            resolution="i",
            interval="1min",
            start_date=(datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d"),
        )
    elif source == "oanda":
        return lib.forex_av_model.get_quote(to_symbol, from_symbol)
    else:
        raise ValueError("Source not supported. Please use 'yf' or 'oanda'.")


##################################################################
#                             Funds                              #
##################################################################


class Funds(Category):
    def __init__(self, *args, **kwargs):
        """Initialize the class"""
        super().__init__(*args, **kwargs)
        self.info = lib.mutual_funds_investpy_model.get_fund_info
        self.info_view = lib.mutual_funds_investpy_view.display_fund_info
        self.overview = lib.mutual_funds_investpy_model.get_overview
        self.overview_view = lib.mutual_funds_investpy_view.display_overview
        self.search = lib.mutual_funds_investpy_model.search_funds
        self.search_view = lib.mutual_funds_investpy_view.display_search


##################################################################
#                             Forex                              #
##################################################################


class ForexOanda(Category):
    def __init__(self, *args, **kwargs):
        """Initialize the class"""
        super().__init__(*args, **kwargs)
        self.fwd = lib.forex_fxempire_model.get_forward_rates
        self.fwd_view = lib.forex_fxempire_view.display_forward_rates
        self.summary = lib.forex_oanda_model.account_summary_request
        self.summary_view = lib.forex_oanda_view.get_account_summary
        self.cancel = lib.forex_oanda_model.cancel_pending_order_request
        self.cancel_view = lib.forex_oanda_view.cancel_pending_order
        self.close = lib.forex_oanda_model.close_trades_request
        self.close_view = lib.forex_oanda_view.close_trade
        self.order = lib.forex_oanda_model.create_order_request
        self.order_view = lib.forex_oanda_view.create_order
        self.price = lib.forex_oanda_model.fx_price_request
        self.price_view = lib.forex_oanda_view.get_fx_price
        self.calendar = lib.forex_oanda_model.get_calendar_request
        self.calendar_view = lib.forex_oanda_view.calendar
        self.candles = lib.forex_oanda_model.get_candles_dataframe
        self.candles_view = lib.forex_oanda_view.show_candles
        self.openpositions = lib.forex_oanda_model.open_positions_request
        self.openpositions_view = lib.forex_oanda_view.get_open_positions
        self.opentrades = lib.forex_oanda_model.open_trades_request
        self.opentrades_view = lib.forex_oanda_view.get_open_trades
        self.listorders = lib.forex_oanda_model.order_history_request
        self.listorders_view = lib.forex_oanda_view.list_orders
        self.orderbook = lib.forex_oanda_model.orderbook_plot_data_request
        self.orderbook_view = lib.forex_oanda_view.get_order_book
        self.pending = lib.forex_oanda_model.pending_orders_request
        self.pending_view = lib.forex_oanda_view.get_pending_orders
        self.positionbook = lib.forex_oanda_model.positionbook_plot_data_request
        self.positionbook_view = lib.forex_oanda_view.get_position_book
