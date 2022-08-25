"""Forecast API."""
import os
from openbb_terminal.helper_classes import ModelsNamespace as _models

# flake8: noqa
# pylint: disable=unused-import,wrong-import-order

# Menu commands
from .forecast_model import load
from .forecast_view import show_df as show
from .forecast_view import display_plot as plot
from .forecast_model import clean
from .forecast_model import combine_dfs as combine
from .forecast_view import describe_df as desc
from .forecast_view import display_corr as corr
from .forecast_view import display_seasonality as season
from .forecast_model import delete_column as delete
from .forecast_model import rename_column as rename
from .forecast_view import export_df as export
from .forecast_model import add_signal as signal
from .forecast_model import add_atr as atr
from .forecast_model import add_ema as ema
from .forecast_model import add_sto as sto
from .forecast_model import add_rsi as rsi
from .forecast_model import add_roc as roc
from .forecast_model import add_momentum as mom
from .forecast_model import add_delta as delta
from .expo_view import display_expo_forecast as expo
from .theta_view import display_theta_forecast as theta
from .linregr_view import display_linear_regression as linregr
from .regr_view import display_regression as regr
from .rnn_view import display_rnn_forecast as rnn
from .brnn_view import display_brnn_forecast as brnn
from .nbeats_view import display_nbeats_forecast as nbeats
from .tcn_view import display_tcn_forecast as tcn
from .trans_view import display_trans_forecast as trans
from .tft_view import display_tft_forecast as tft


# Models
models = _models(os.path.abspath(os.path.dirname(__file__)))
