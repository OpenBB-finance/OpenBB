# flake8: noqa
# pylint: disable=C0301,R0902,R0903
from openbb_terminal.sdk_core.sdk_helpers import Category
import openbb_terminal.sdk_core.sdk_init as lib


class ForexRoot(Category):
    """OpenBB SDK Forex Module

    Attributes:
        `candle`: Show candle plot for fx data.\n
        `get_currency_list`: Load AV currency codes from a local file.\n
        `hist`: Get historical forex data.\n
        `load`: Load forex for two given symbols.\n
        `quote`: Get current exchange rate quote from alpha vantage.\n
        `quote_view`: Display current forex pair exchange rate.\n
    """

    def __init__(self):
        super().__init__()
        self.candle = lib.forex_helpers.display_candle
        self.get_currency_list = lib.forex_av_model.get_currency_list
        self.hist = lib.forex_av_model.get_historical
        self.load = lib.forex_helpers.load
        self.quote = lib.forex_av_model.get_quote
        self.quote_view = lib.forex_av_view.display_quote


class ForexOanda(Category):
    """OpenBB SDK Oanda Module.

    Attributes:
        `calendar`: Request data of significant events calendar.\n
        `calendar_view`: View calendar of significant events.\n
        `cancel`: Request cancellation of a pending order.\n
        `cancel_view`: Cancel a Pending Order.\n
        `candles`: Request data for candle chart.\n
        `candles_view`: Show candle chart.\n
        `close`: Close a trade.\n
        `close_view`: Close a trade.\n
        `fwd`: Gets forward rates from fxempire\n
        `fwd_view`: Display forward rates for currency pairs\n
        `listorders`: Request the orders list from Oanda.\n
        `listorders_view`: List order history.\n
        `openpositions`: Request information on open positions.\n
        `openpositions_view`: Get information about open positions.\n
        `opentrades`: Request open trades data.\n
        `opentrades_view`: View open trades.\n
        `order`: Request creation of buy/sell trade order.\n
        `order_view`: Create a buy/sell order.\n
        `orderbook`: Request order book data for plotting.\n
        `orderbook_view`: Plot the orderbook for the instrument if Oanda provides one.\n
        `pending`: Request information on pending orders.\n
        `pending_view`: Get information about pending orders.\n
        `positionbook`: Request position book data for plotting.\n
        `positionbook_view`: Plot a position book for an instrument if Oanda provides one.\n
        `price`: Request price for a forex pair.\n
        `price_view`: View price for loaded currency pair.\n
        `summary`: Request Oanda account summary.\n
        `summary_view`: Print Oanda account summary.\n
    """

    def __init__(self):
        super().__init__()
        self.calendar = lib.forex_oanda_model.get_calendar_request
        self.calendar_view = lib.forex_oanda_view.calendar
        self.cancel = lib.forex_oanda_model.cancel_pending_order_request
        self.cancel_view = lib.forex_oanda_view.cancel_pending_order
        self.candles = lib.forex_oanda_model.get_candles_dataframe
        self.candles_view = lib.forex_oanda_view.show_candles
        self.close = lib.forex_oanda_model.close_trades_request
        self.close_view = lib.forex_oanda_view.close_trade
        self.fwd = lib.forex_fxempire_model.get_forward_rates
        self.fwd_view = lib.forex_fxempire_view.display_forward_rates
        self.listorders = lib.forex_oanda_model.order_history_request
        self.listorders_view = lib.forex_oanda_view.list_orders
        self.openpositions = lib.forex_oanda_model.open_positions_request
        self.openpositions_view = lib.forex_oanda_view.get_open_positions
        self.opentrades = lib.forex_oanda_model.open_trades_request
        self.opentrades_view = lib.forex_oanda_view.get_open_trades
        self.order = lib.forex_oanda_model.create_order_request
        self.order_view = lib.forex_oanda_view.create_order
        self.orderbook = lib.forex_oanda_model.orderbook_plot_data_request
        self.orderbook_view = lib.forex_oanda_view.get_order_book
        self.pending = lib.forex_oanda_model.pending_orders_request
        self.pending_view = lib.forex_oanda_view.get_pending_orders
        self.positionbook = lib.forex_oanda_model.positionbook_plot_data_request
        self.positionbook_view = lib.forex_oanda_view.get_position_book
        self.price = lib.forex_oanda_model.fx_price_request
        self.price_view = lib.forex_oanda_view.get_fx_price
        self.summary = lib.forex_oanda_model.account_summary_request
        self.summary_view = lib.forex_oanda_view.get_account_summary
