# ######### THIS FILE IS AUTO GENERATED - ANY CHANGES WILL BE VOID ######### #
# flake8: noqa
# pylint: disable=C0301,R0902,R0903
from openbb_terminal.core.sdk.sdk_helpers import Category
import openbb_terminal.core.sdk.sdk_init as lib


class ForexRoot(Category):
    """Forex Module

    Attributes:
        `candle`: Show candle plot for fx data.\n
        `fwd`: Gets forward rates from fxempire\n
        `get_currency_list`: Load AV currency codes from a local file.\n
        `load`: Load forex for two given symbols.\n
        `quote`: Get forex quote.\n
    """

    _location_path = "forex"

    def __init__(self):
        super().__init__()
        self.candle = lib.forex_helper.display_candle
        self.fwd = lib.forex_fxempire_model.get_forward_rates
        self.get_currency_list = lib.forex_av_model.get_currency_list
        self.load = lib.forex_helper.load
        self.quote = lib.forex_sdk_helpers.quote


class ForexOanda(Category):
    """Oanda Module.

    Attributes:
        `calendar`: Request data of significant events calendar.\n
        `calendar_chart`: View calendar of significant events.\n
        `cancel`: Request cancellation of a pending order.\n
        `cancel_chart`: Cancel a Pending Order.\n
        `candles`: Request data for candle chart.\n
        `candles_chart`: Show candle chart.\n
        `close`: Close a trade.\n
        `close_chart`: Close a trade.\n
        `listorders`: Request the orders list from Oanda.\n
        `listorders_chart`: List order history.\n
        `openpositions`: Request information on open positions.\n
        `openpositions_chart`: Get information about open positions.\n
        `opentrades`: Request open trades data.\n
        `opentrades_chart`: View open trades.\n
        `order`: Request creation of buy/sell trade order.\n
        `order_chart`: Create a buy/sell order.\n
        `orderbook`: Request order book data for plotting.\n
        `orderbook_chart`: Plot the orderbook for the instrument if Oanda provides one.\n
        `pending`: Request information on pending orders.\n
        `pending_chart`: Get information about pending orders.\n
        `positionbook`: Request position book data for plotting.\n
        `positionbook_chart`: Plot a position book for an instrument if Oanda provides one.\n
        `price`: Request price for a forex pair.\n
        `price_chart`: View price for loaded currency pair.\n
        `summary`: Request Oanda account summary.\n
        `summary_chart`: Print Oanda account summary.\n
    """

    _location_path = "forex.oanda"

    def __init__(self):
        super().__init__()
        self.calendar = lib.forex_oanda_model.get_calendar_request
        self.calendar_chart = lib.forex_oanda_view.calendar
        self.cancel = lib.forex_oanda_model.cancel_pending_order_request
        self.cancel_chart = lib.forex_oanda_view.cancel_pending_order
        self.candles = lib.forex_oanda_model.get_candles_dataframe
        self.candles_chart = lib.forex_oanda_view.show_candles
        self.close = lib.forex_oanda_model.close_trades_request
        self.close_chart = lib.forex_oanda_view.close_trade
        self.listorders = lib.forex_oanda_model.order_history_request
        self.listorders_chart = lib.forex_oanda_view.list_orders
        self.openpositions = lib.forex_oanda_model.open_positions_request
        self.openpositions_chart = lib.forex_oanda_view.get_open_positions
        self.opentrades = lib.forex_oanda_model.open_trades_request
        self.opentrades_chart = lib.forex_oanda_view.get_open_trades
        self.order = lib.forex_oanda_model.create_order_request
        self.order_chart = lib.forex_oanda_view.create_order
        self.orderbook = lib.forex_oanda_model.orderbook_plot_data_request
        self.orderbook_chart = lib.forex_oanda_view.get_order_book
        self.pending = lib.forex_oanda_model.pending_orders_request
        self.pending_chart = lib.forex_oanda_view.get_pending_orders
        self.positionbook = lib.forex_oanda_model.positionbook_plot_data_request
        self.positionbook_chart = lib.forex_oanda_view.get_position_book
        self.price = lib.forex_oanda_model.fx_price_request
        self.price_chart = lib.forex_oanda_view.get_fx_price
        self.summary = lib.forex_oanda_model.account_summary_request
        self.summary_chart = lib.forex_oanda_view.get_account_summary
