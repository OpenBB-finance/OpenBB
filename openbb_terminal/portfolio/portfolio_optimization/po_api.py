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
    display_min_risk as min_risk,
)
from openbb_terminal.portfolio.portfolio_optimization.optimizer_view import (
    display_max_util as max_util,
)
from openbb_terminal.portfolio.portfolio_optimization.optimizer_view import (
    display_max_ret as max_ret,
)
from openbb_terminal.portfolio.portfolio_optimization.optimizer_view import (
    display_max_div as max_div,
)
from openbb_terminal.portfolio.portfolio_optimization.optimizer_view import (
    display_max_decorr as max_decorr,
)
from openbb_terminal.portfolio.portfolio_optimization.optimizer_view import (
    display_ef as ef,
)
from openbb_terminal.portfolio.portfolio_optimization.optimizer_view import (
    display_risk_parity as risk_parity,
)
from openbb_terminal.portfolio.portfolio_optimization.optimizer_view import (
    display_rel_risk_parity as rel_risk_parity,
)
from openbb_terminal.portfolio.portfolio_optimization.optimizer_view import (
    display_hrp as hrp,
)
from openbb_terminal.portfolio.portfolio_optimization.optimizer_view import (
    display_herc as herc,
)
from openbb_terminal.portfolio.portfolio_optimization.optimizer_view import (
    display_nco as nco,
)

# Models
models = _models(os.path.abspath(os.path.dirname(__file__)))
