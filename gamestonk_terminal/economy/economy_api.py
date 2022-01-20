"""Economy context API."""
import os
from gamestonk_terminal.helper_classes import ModelsNamespace as _models

# flake8: noqa
# pylint: disable=unused-import

# Context menus
from .cnn_view import fear_and_greed_index as feargreed
from .wsj_view import display_overview as overview
from .wsj_view import display_indices as indices
from .wsj_view import display_futures as futures
from .wsj_view import display_usbonds as usbonds
from .wsj_view import display_glbonds as glbonds
from .wsj_view import display_currencies as currencies
from .finviz_view import display_future as future

# The one below is different because map is a python reserved word
from .finviz_view import map_sp500_view as map_sp500
from .finviz_view import display_valuation as valuation
from .finviz_view import display_performance as performance
from .finviz_view import display_spectrum as spectrum
from .alphavantage_view import realtime_performance_sector as rtps
from .alphavantage_view import display_real_gdp as gdp
from .alphavantage_view import display_gdp_capita as gdpc
from .alphavantage_view import display_inflation as inf
from .alphavantage_view import display_cpi as cpi
from .alphavantage_view import display_treasury_yield as tyld
from .alphavantage_view import display_unemployment as unemp
from .nasdaq_view import display_big_mac_index as bigmac
from .fred import fred_api as fred

# Models
models = _models(os.path.abspath(os.path.dirname(__file__)))
