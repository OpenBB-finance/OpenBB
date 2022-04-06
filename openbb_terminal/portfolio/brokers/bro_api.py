"""Brokers context API."""
import os
from openbb_terminal.helper_classes import ModelsNamespace as _models

# flake8: noqa
# pylint: disable=unused-import

# Context menus
from .ally import ally_api as ally
from .coinbase import coinbase_api as cb
from .robinhood import robinhood_api as rh
from .degiro import degiro_api as degiro

# Models
models = _models(os.path.abspath(os.path.dirname(__file__)))
