"""Discovery API."""
import os as _os
import importlib.machinery as _machinery
import importlib.util as _util

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
# pylint: disable=too-few-public-methods
class _models:
    """A namespace placeholder for the menu models."""

    def __init__(self) -> None:
        """Import all menu models into the models namespace."""
        _menu_models = [
            (
                f.replace("_model.py", ""),
                _os.path.abspath(_os.path.join(_os.path.dirname(__file__), f)),
            )
            for f in _os.listdir(_os.path.dirname(__file__))
            if f.endswith("_model.py")
        ]

        for _model_name, _model_file in _menu_models:
            _loader = _machinery.SourceFileLoader(_model_name, _model_file)
            _spec = _util.spec_from_loader(_model_name, _loader)
            if _spec is not None:
                setattr(self, _model_name, _util.module_from_spec(_spec))
                _loader.exec_module(getattr(self, _model_name))
            else:
                pass


models = _models()
