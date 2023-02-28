# ######### THIS FILE IS AUTO GENERATED - ANY CHANGES WILL BE VOID ######### #
# flake8: noqa
# pylint: disable=C0301,R0902,R0903
from openbb_terminal.core.sdk.models import forex_sdk_model as model


class ForexController(model.ForexRoot):
    """Forex Module.

    Submodules:
        `oanda`: Oanda Module

    Attributes:
        `candle`: Show candle plot for fx data.\n
        `fwd`: Gets forward rates from fxempire\n
        `get_currency_list`: Load AV currency codes from a local file.\n
        `load`: Load forex for two given symbols.\n
        `quote`: Get forex quote.\n
    """

    @property
    def oanda(self):
        """Forex Oanda Submodule

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

        return model.ForexOanda()
