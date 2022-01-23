"""Mutual fund context API."""
import os
from gamestonk_terminal.helper_classes import ModelsNamespace as _models

# flake8: noqa
# pylint: disable=unused-import

# Context menus
from .investpy_view import display_search as search
from .investpy_view import display_overview as overview
from .investpy_view import display_fund_info as info
from .investpy_view import display_historical as plot
from .yfinance_view import display_sector as sector
from .yfinance_view import display_equity as equity

# Models
models = _models(os.path.abspath(os.path.dirname(__file__)))
