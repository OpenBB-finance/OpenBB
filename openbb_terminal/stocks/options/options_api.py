"""Options API."""

# flake8: noqa
# pylint: disable=unused-import


import os

from openbb_terminal.helper_classes import ModelsNamespace as _models

from .alphaquery_view import display_put_call_ratio as pcr
from .barchart_view import print_options_data as info

# Menu commands
from .calculator_view import view_calculator as calc
from .chartexchange_view import display_raw as hist_ce
from .fdscanner_view import display_options as unu
from .screen.syncretism_view import view_historical_greeks as grhist
from .tradier_view import display_chains as chains
from .tradier_view import display_expirations as exp
from .tradier_view import display_historical as hist_tr
from .tradier_view import plot_oi as oi_tr
from .tradier_view import plot_vol as vol_tr
from .tradier_view import plot_volume_open_interest as voi_tr
from .yfinance_view import display_vol_surface as vsurf
from .yfinance_view import plot_oi as oi_yf
from .yfinance_view import plot_plot as plot
from .yfinance_view import plot_vol as vol_yf
from .yfinance_view import plot_volume_open_interest as voi_yf
from .yfinance_view import show_binom as binom
from .yfinance_view import show_greeks as greeks
from .yfinance_view import show_parity as parity

# flake8: noqa
# pylint: disable=unused-import


# Models
models = _models(os.path.abspath(os.path.dirname(__file__)))
