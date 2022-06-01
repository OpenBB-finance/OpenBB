"""Forecasting API."""
import os
from openbb_terminal.helper_classes import ModelsNamespace as _models

# flake8: noqa
# pylint: disable=unused-import,wrong-import-order

# Menu commands
from .forecasting_model import load
from .forecasting_model import clean
from .forecasting_view import show_options as options
from .forecasting_view import display_plot as plot

# Models
models = _models(os.path.abspath(os.path.dirname(__file__)))
