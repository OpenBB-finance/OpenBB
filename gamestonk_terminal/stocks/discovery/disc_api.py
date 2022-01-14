"""Discovery API."""
import os
from gamestonk_terminal.helper_classes import ModelsNamespace as _models

# flake8: noqa
# pylint: disable=unused-import

# Menu commands
from .geekofwallstreet_view import display_realtime_earnings as rtearn
from .finnhub_view import past_ipo as pipo
from .finnhub_view import future_ipo as fipo
from .yahoofinance_view import display_gainers as gainers
from .yahoofinance_view import display_losers as losers
from .yahoofinance_view import display_ugs as ugs
from .yahoofinance_view import display_gtech as gtech
from .yahoofinance_view import display_active as active
from .yahoofinance_view import display_ulc as ulc
from .yahoofinance_view import display_asc as asc
from .fidelity_view import orders_view as ford
from .ark_view import ark_orders_view as arkord
from .seeking_alpha_view import upcoming_earning_release_dates as upcoming
from .seeking_alpha_view import news as trending
from .shortinterest_view import low_float as lowfloat
from .seeking_alpha_view import display_news as cnews
from .shortinterest_view import hot_penny_stocks as hotpenny
from .nasdaq_view import display_top_retail as rtat

# Models
models = _models(os.path.abspath(os.path.dirname(__file__)))
