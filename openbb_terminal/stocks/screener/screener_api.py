"""Screener API."""
import os
from openbb_terminal.helper_classes import ModelsNamespace as _models

# flake8: noqa
# pylint: disable=unused-import

# Menu commands
from .yahoofinance_view import historical
from .finviz_view import screener as finviz_screener

# Models
models = _models(os.path.abspath(os.path.dirname(__file__)))
