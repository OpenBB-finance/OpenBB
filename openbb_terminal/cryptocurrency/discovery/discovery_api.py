"""Discovery context API."""
import os
from openbb_terminal.helper_classes import ModelsNamespace as _models

# flake8: noqa
# pylint: disable=unused-import

# Menu commands
from .pycoingecko_view import display_gainers as cggainers
from .pycoingecko_view import display_losers as cglosers
from .coinmarketcap_view import display_cmc_top_coins as cmctop
from .coinpaprika_view import display_search_results as cpsearch


# Models
models = _models(os.path.abspath(os.path.dirname(__file__)))
