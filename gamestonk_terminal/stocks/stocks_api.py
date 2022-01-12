"""Stocks context API."""
# flake8: noqa
# pylint: disable=unused-import

# Context root level functions
from gamestonk_terminal.common.newsapi_view import news
from .stocks_helper import load, process_candle, search, quote
from .stocks_helper import display_candle as candle

# Context menus
from .backtesting import bt_api as bt
from .behavioural_analysis import ba_api as ba
from .comparison_analysis import ca_api as ca
from .discovery import disc_api as disc
from .due_diligence import dd_api as dd
