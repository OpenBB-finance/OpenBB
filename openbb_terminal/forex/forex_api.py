"""Forex context API."""
import os
from openbb_terminal.helper_classes import ModelsNamespace as _models

# flake8: noqa
# pylint: disable=unused-import

# Context menus
from .forex_helper import display_candle as candle
from .av_view import display_quote as quote
from .technical_analysis import ta_api as ta
from .oanda import oanda_api as oanda

# Models
models = _models(os.path.abspath(os.path.dirname(__file__)))
