"""Backtesting API."""
import os
from openbb_terminal.helper_classes import ModelsNamespace as _models

# flake8: noqa
# pylint: disable=unused-import

# Menu commands
from .bt_view import display_whatif_scenario as whatif
from .bt_view import display_simple_ema as ema
from .bt_view import display_ema_cross as ema_cross
from .bt_view import display_rsi_strategy as rsi

# Models
models = _models(os.path.abspath(os.path.dirname(__file__)))
