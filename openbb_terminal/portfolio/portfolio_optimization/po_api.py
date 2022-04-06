"""Portfolio optimization context API."""
import os
from openbb_terminal.helper_classes import ModelsNamespace as _models

# flake8: noqa
# pylint: disable=unused-import

# Context menus
from openbb_terminal.portfolio.portfolio_optimization.optimizer_view import (
    display_equal_weight as equal,
)
from openbb_terminal.portfolio.portfolio_optimization.optimizer_view import (
    display_property_weighting as weighting,
)
from openbb_terminal.portfolio.portfolio_optimization.optimizer_view import (
    display_max_sharpe as max_sharpe,
)
from openbb_terminal.portfolio.portfolio_optimization.optimizer_view import (
    display_min_volatility as min_vol,
)
from openbb_terminal.portfolio.portfolio_optimization.optimizer_view import (
    display_max_quadratic_utility as maxquadutil,
)
from openbb_terminal.portfolio.portfolio_optimization.optimizer_view import (
    display_efficient_risk as effrisk,
)
from openbb_terminal.portfolio.portfolio_optimization.optimizer_view import (
    display_efficient_return as effret,
)
from openbb_terminal.portfolio.portfolio_optimization.optimizer_view import (
    display_ef as ef,
)

# Models
models = _models(os.path.abspath(os.path.dirname(__file__)))
