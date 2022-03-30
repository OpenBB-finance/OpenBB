"""Insider Trading API."""
import os
from openbb_terminal.helper_classes import ModelsNamespace as _models

# flake8: noqa
# pylint: disable=unused-import

# Menu commands
from .openinsider_view import print_insider_data
from .businessinsider_view import insider_activity as act
from .finviz_view import last_insider_activity as lins

# Models
models = _models(os.path.abspath(os.path.dirname(__file__)))
