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
from .fundamental_analysis import fa_api as fa
from .government import gov_api as gov
from .insider import insider_api as ins
from .options import options_api as options
from .quantitative_analysis import qa_api as qa
from .screener import screener_api as screener
from .sector_industry_analysis import sia_api as sia
from .technical_analysis import ta_api as ta

try:
    from .prediction_techniques import pred_api as pred
except Exception:
    pass
    # print("Prediction API is not available.")
