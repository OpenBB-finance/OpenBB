# flake8: noqa
# pylint: disable=C0301,R0902,R0903
from openbb_terminal.sdk_core.sdk_helpers import Category
import openbb_terminal.sdk_core.sdk_init as lib


class FuturesRoot(Category):
    """Futures Module

    Attributes:
        `curve`: Get curve futures [Source: Yahoo Finance]\n
        `curve_chart`: Display curve futures [Source: Yahoo Finance]\n
        `historical`: Get historical futures [Source: Yahoo Finance]\n
        `historical_chart`: Display historical futures [Source: Yahoo Finance]\n
        `search`: Get search futures [Source: Yahoo Finance]\n
    """

    _location_path = "futures"

    def __init__(self):
        super().__init__()
        self.curve = lib.futures_yfinance_model.get_curve_futures
        self.curve_chart = lib.futures_yfinance_view.display_curve
        self.historical = lib.futures_yfinance_model.get_historical_futures
        self.historical_chart = lib.futures_yfinance_view.display_historical
        self.search = lib.futures_yfinance_model.get_search_futures
