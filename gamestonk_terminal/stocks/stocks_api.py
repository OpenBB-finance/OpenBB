"""Stocks context API."""
# flake8: noqa
# pylint: disable=unused-import

# Context root level functions
from gamestonk_terminal.common.newsapi_view import news
from .stocks_helper import load, process_candle, search, quote
from .stocks_helper import display_candle as candle

# Context menus
from .discovery import disc_api as disc
