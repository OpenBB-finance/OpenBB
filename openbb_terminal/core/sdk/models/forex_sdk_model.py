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
