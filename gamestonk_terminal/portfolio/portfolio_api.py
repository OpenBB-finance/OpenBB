"""Portfolio context API."""
import os
from gamestonk_terminal.helper_classes import ModelsNamespace as _models

# flake8: noqa
# pylint: disable=unused-import

# Context menus
from .brokers import bro_api as bro
from .portfolio_analysis import pa_api as pa
from .portfolio_optimization import po_api as po

# from .portfolio_view import Report as ar
# from .portfolio_view import plot_overall_return as rmr

# Models
models = _models(os.path.abspath(os.path.dirname(__file__)))
