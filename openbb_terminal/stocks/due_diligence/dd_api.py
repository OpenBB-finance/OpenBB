"""Due Diligence API."""
import os
from openbb_terminal.helper_classes import ModelsNamespace as _models

# flake8: noqa
# pylint: disable=unused-import

# Menu commands
from .finviz_view import analyst
from .business_insider_view import price_target_from_analysts as pt
from .business_insider_view import estimates as est
from .finnhub_view import rating_over_time as rot
from .fmp_view import rating
from .marketwatch_view import sec_filings as sec
from .csimarket_view import suppliers as supplier
from .csimarket_view import customers as customer
from .ark_view import display_ark_trades as arktrades

# Models
models = _models(os.path.abspath(os.path.dirname(__file__)))
