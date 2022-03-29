"""Fundamental Analysis API."""
import os
from openbb_terminal.helper_classes import ModelsNamespace as _models

# flake8: noqa
# pylint: disable=unused-import

# Menu commands
from .eclect_us_view import display_analysis as analysis
from .business_insider_view import display_management as mgmt
from .finviz_view import display_screen_data as data
from .financial_modeling_prep.fmp_view import valinvest_score as score
from .yahoo_finance_view import display_info as info
from .yahoo_finance_view import display_shareholders as shrs
from .yahoo_finance_view import display_sustainability as sust
from .yahoo_finance_view import display_calendar_earnings as cal
from .yahoo_finance_view import open_web as web
from .yahoo_finance_view import open_headquarters_map as hq
from .yahoo_finance_view import display_dividends as divs
from .av_view import display_overview as overview
from .av_view import display_key as key
from .av_view import display_income_statement as income
from .av_view import display_balance_sheet as balance
from .av_view import display_cash_flow as cash
from .av_view import display_earnings as earnings
from .av_view import display_fraud as fraud
from .dcf_view import CreateExcelFA as dcf
from .market_watch_view import display_sean_seah_warnings as warnings

# Submenus
from .financial_modeling_prep import fmp_api as fmp

# Models
models = _models(os.path.abspath(os.path.dirname(__file__)))
