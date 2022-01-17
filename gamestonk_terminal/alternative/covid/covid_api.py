"""Insider Trading API."""
import os
from gamestonk_terminal.helper_classes import ModelsNamespace as _models

# flake8: noqa
# pylint: disable=unused-import

# Menu commands
from gamestonk_terminal.alternative.covid.covid_view import display_covid_ov as ov
from gamestonk_terminal.alternative.covid.covid_view import display_covid_stat as stat
from gamestonk_terminal.alternative.covid.covid_view import (
    display_country_slopes as slopes,
)


# Models
models = _models(os.path.abspath(os.path.dirname(__file__)))
