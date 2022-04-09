"""Coinbase API."""
import os
from openbb_terminal.helper_classes import ModelsNamespace as _models

# flake8: noqa
# pylint: disable=unused-import

# Context menus
from openbb_terminal.portfolio.brokers.coinbase.coinbase_view import (
    display_account as account,
)
from openbb_terminal.portfolio.brokers.coinbase.coinbase_view import (
    display_history as history,
)
from openbb_terminal.portfolio.brokers.coinbase.coinbase_view import (
    display_orders as orders,
)
from openbb_terminal.portfolio.brokers.coinbase.coinbase_view import (
    display_deposits as deposits,
)

# Models
models = _models(os.path.abspath(os.path.dirname(__file__)))
