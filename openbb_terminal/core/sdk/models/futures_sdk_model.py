# ######### THIS FILE IS AUTO GENERATED - ANY CHANGES WILL BE VOID ######### #
# flake8: noqa
# pylint: disable=C0301,R0902,R0903
from openbb_terminal.core.sdk.sdk_helpers import Category
import openbb_terminal.core.sdk.sdk_init as lib


class FuturesRoot(Category):
    """Futures Module

    Attributes:
        `curve`: Get curve futures [Source: Yahoo Finance]\n
        `curve_chart`: Display curve futures [Source: Yahoo Finance]\n
        `historical`: Get historical futures data\n
        `historical_chart`: Display historical futures [Source: Yahoo Finance]\n
        `search`: Get search futures [Source: Yahoo Finance]\n
    """

    _location_path = "futures"

    def __init__(self):
        super().__init__()
        self.curve = lib.futures_yfinance_model.get_curve_futures
        self.curve_chart = lib.futures_yfinance_view.display_curve
        self.historical = lib.futures_sdk_model.get_historical
        self.historical_chart = lib.futures_yfinance_view.display_historical
        self.search = lib.futures_yfinance_model.get_search_futures
