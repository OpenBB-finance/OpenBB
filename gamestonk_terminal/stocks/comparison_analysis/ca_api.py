"""Comparison Analysis API."""
import os
from gamestonk_terminal.helper_classes import ModelsNamespace as _models

# flake8: noqa
# pylint: disable=unused-import

# Menu commands
from .yahoo_finance_view import display_historical as hist
from .yahoo_finance_view import display_correlation as hcorr
from .yahoo_finance_view import display_volume as volume
from .marketwatch_view import display_income_comparison as income
from .marketwatch_view import display_balance_comparison as balance
from .marketwatch_view import display_cashflow_comparison as cashflow
from .finbrain_view import display_sentiment_compare as sentiment
from .finbrain_view import display_sentiment_correlation as scorr
from .finviz_compare_view import screener
from .finviz_compare_model import get_similar_companies as getfinviz
from .finnhub_model import get_similar_companies as getfinnhub


# Models
models = _models(os.path.abspath(os.path.dirname(__file__)))
