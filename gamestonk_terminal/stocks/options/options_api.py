"""Options API."""
import os
from gamestonk_terminal.helper_classes import ModelsNamespace as _models

# flake8: noqa
# pylint: disable=unused-import

# Menu commands
from .calculator_view import view_calculator as calc
from .fdscanner_view import display_options as unu
from .alphaquery_view import display_put_call_ratio as pcr
from .barchart_view import print_options_data as info
from .syncretism_view import view_historical_greeks as grhist
from .chartexchange_view import display_raw as hist_ce
from .tradier_view import display_historical as hist_tr
from .tradier_view import display_chains as chains
from .tradier_view import plot_vol as vol_tr
from .yfinance_view import plot_vol as vol_yf
from .tradier_view import plot_volume_open_interest as voi_tr
from .yfinance_view import plot_volume_open_interest as voi_yf
from .tradier_view import plot_oi as oi_tr
from .yfinance_view import plot_oi as oi_yf
from .yfinance_view import plot_plot as plot
from .yfinance_view import show_parity as parity
from .yfinance_view import show_binom as binom


# Models
models = _models(os.path.abspath(os.path.dirname(__file__)))
