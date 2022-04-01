"""Econometrics API."""
import os
from openbb_terminal.helper_classes import ModelsNamespace as _models

# flake8: noqa
# pylint: disable=unused-import,wrong-import-order

# Menu commands
from .econometrics_model import load
from .econometrics_model import clean
from .econometrics_view import show_options as options
from .econometrics_view import get_plot as plot
from .regression_model import get_ols as ols
from .econometrics_view import display_norm as norm
from .econometrics_view import display_root as root
from .regression_view import display_panel as panel
from .regression_model import get_comparison as compare
from .regression_view import display_dwat as dwat
from .regression_view import display_bgod as bgod
from .regression_view import display_bpag as bpag
from .econometrics_view import display_granger as granger
from .econometrics_view import display_cointegration_test as coint

# Models
models = _models(os.path.abspath(os.path.dirname(__file__)))
