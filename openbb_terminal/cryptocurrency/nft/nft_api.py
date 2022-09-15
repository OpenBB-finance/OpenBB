"""NFT context API."""
import os
from openbb_terminal.helper_classes import ModelsNamespace as _models

# flake8: noqa
# pylint: disable=unused-import

# Menu commands
from .opensea_view import display_collection_stats as stats

# Models
models = _models(os.path.abspath(os.path.dirname(__file__)))
