"""Financial Modeling Prep API."""
import os
from openbb_terminal.helper_classes import ModelsNamespace as _models

# flake8: noqa
# pylint: disable=unused-import

# Menu commands
from .fmp_view import display_profile as profile
from .fmp_view import display_quote as quote
from .fmp_view import display_enterprise as enterprise
from .fmp_view import display_discounted_cash_flow as dcf
from .fmp_view import display_income_statement as income
from .fmp_view import display_balance_sheet as balance
from .fmp_view import display_cash_flow as cash
from .fmp_view import display_key_metrics as metrics
from .fmp_view import display_financial_ratios as ratios
from .fmp_view import display_financial_statement_growth as growth


# Models
models = _models(os.path.abspath(os.path.dirname(__file__)))
