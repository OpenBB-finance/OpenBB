"""ETF context API."""
import os
from gamestonk_terminal.helper_classes import ModelsNamespace as _models

# flake8: noqa
# pylint: disable=unused-import

# Context menus
from gamestonk_terminal.common.newsapi_view import news
from .financedatabase_view import display_etf_by_name as ln
from .financedatabase_view import display_etf_by_description as ld
from .stockanalysis_view import view_overview as overview
from .stockanalysis_view import view_holdings as holdings
from .yfinance_view import display_etf_weightings as weights
from .yfinance_view import display_etf_description as summary
from .technical_analysis import ta_api as ta
from .screener import screener_api as scr
from .discovery import disc_api as disc

try:
    from .prediction_techniques import pred_api as pred
except Exception:
    pass

# Models
models = _models(os.path.abspath(os.path.dirname(__file__)))
