"""Discovery context API."""
import os
from gamestonk_terminal.helper_classes import ModelsNamespace as _models

# flake8: noqa
# pylint: disable=unused-import

# Menu commands
from .pycoingecko_view import display_gainers as cggainers
from .pycoingecko_view import display_losers as cglosers
from .pycoingecko_view import display_top_volume_coins as cgvolume
from .pycoingecko_view import display_top_defi_coins as cgdefi
from .coinmarketcap_view import display_cmc_top_coins as cmctop
from .coinpaprika_view import display_search_results as cpsearch


# Models
models = _models(os.path.abspath(os.path.dirname(__file__)))
