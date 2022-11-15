# flake8: noqa
# pylint: disable=C0301,R0902,R0903
from openbb_terminal.sdk_core.models import forex_sdk_model as model


class ForexController(model.ForexRoot):
    """OpenBB SDK Forex Module.

    Submodules:
        `oanda`: Oanda Module

    Attributes:
        `candle`: Show candle plot for fx data.\n
        `get_currency_list`: Load AV currency codes from a local file.\n
        `hist`: Get historical forex data.\n
        `load`: Load forex for two given symbols.\n
        `quote`: Get current exchange rate quote from alpha vantage.\n
        `quote_view`: Display current forex pair exchange rate.\n
    """

    @property
    def oanda(self):
        """OpenBB SDK Forex Oanda Submodule

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
            `orderbook_chart`: Plot the orderbook for the instrument if Oanda provides one.\n
            `pending`: Request information on pending orders.\n
            `pending_view`: Get information about pending orders.\n
            `positionbook`: Request position book data for plotting.\n
            `positionbook_chart`: Plot a position book for an instrument if Oanda provides one.\n
            `price`: Request price for a forex pair.\n
            `price_view`: View price for loaded currency pair.\n
            `summary`: Request Oanda account summary.\n
            `summary_print`: Print Oanda account summary.\n
        """

        return model.ForexOanda()
