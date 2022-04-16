"""Tools context API."""
import os
from openbb_terminal.helper_classes import ModelsNamespace as _models

# flake8: noqa
# pylint: disable=unused-import

# Menu commands
from .tools_view import display_apy as aprtoapy
from .tools_view import display_il as il

# Models
models = _models(os.path.abspath(os.path.dirname(__file__)))
