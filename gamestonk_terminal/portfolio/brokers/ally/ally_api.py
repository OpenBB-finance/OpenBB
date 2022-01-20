"""Allycontext API."""
import os
from gamestonk_terminal.helper_classes import ModelsNamespace as _models

# flake8: noqa
# pylint: disable=unused-import

# Context menus
from gamestonk_terminal.portfolio.brokers.ally.ally_view import (
    display_holdings as holdings,
)
from gamestonk_terminal.portfolio.brokers.ally.ally_view import (
    display_history as history,
)
from gamestonk_terminal.portfolio.brokers.ally.ally_view import (
    display_balances as balances,
)
from gamestonk_terminal.portfolio.brokers.ally.ally_view import (
    display_stock_quote as quote,
)
from gamestonk_terminal.portfolio.brokers.ally.ally_view import (
    display_top_lists as movers,
)

# Models
models = _models(os.path.abspath(os.path.dirname(__file__)))
