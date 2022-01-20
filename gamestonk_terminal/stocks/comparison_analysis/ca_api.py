"""Comparison Analysis API."""
import os
from gamestonk_terminal.helper_classes import ModelsNamespace as _models

# flake8: noqa
# pylint: disable=unused-import

# Menu commands
# print("Comparison Analysis Warning.")
# print("Menu commands API is awaiting for comparison_analysis module refactoring.")
# print("Only data models can be used at this moment.")

# Models
models = _models(os.path.abspath(os.path.dirname(__file__)))
