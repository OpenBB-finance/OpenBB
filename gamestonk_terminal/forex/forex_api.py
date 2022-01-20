"""Forex context API."""
import os
from gamestonk_terminal.helper_classes import ModelsNamespace as _models

# flake8: noqa
# pylint: disable=unused-import

# Context menus
from .av_view import display_candle as candle
from .av_view import display_quote as quote
from .oanda import oanda_api as oanda

# Models
models = _models(os.path.abspath(os.path.dirname(__file__)))
