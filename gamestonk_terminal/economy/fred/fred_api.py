"""Fred context API."""
import os
from gamestonk_terminal.helper_classes import ModelsNamespace as _models

# flake8: noqa
# pylint: disable=unused-import

# Context menus
from .fred_view import notes as search
from .fred_view import display_fred_series as plot


# Models
models = _models(os.path.abspath(os.path.dirname(__file__)))
