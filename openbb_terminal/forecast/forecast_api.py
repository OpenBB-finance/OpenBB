"""Forecast API."""
import os
from openbb_terminal.helper_classes import ModelsNamespace as _models

# flake8: noqa
# pylint: disable=unused-import,wrong-import-order

# Menu commands
from .forecast_model import load
from .forecast_model import clean
from .forecast_view import show_options as options
from .forecast_view import display_plot as plot
from .brnn_view import display_brnn_forecast as brnn
from .expo_view import display_expo_forecast as expo
from .knn_view import display_k_nearest_neighbors as knn
from .linregr_view import display_linear_regression as linregr
from .mc_view import display_mc_forecast as mc
from .nbeats_view import display_nbeats_forecast as nbeats
from .regr_view import display_regression as regr
from .rnn_view import display_rnn_forecast as rnn
from .tcn_view import display_tcn_forecast as tcn
from .tft_view import display_tft_forecast as tft
from .theta_view import display_theta_forecast as theta
from .trans_view import display_trans_forecast as trans


# Models
models = _models(os.path.abspath(os.path.dirname(__file__)))
