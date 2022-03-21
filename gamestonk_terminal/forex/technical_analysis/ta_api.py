"""TA context API."""
import os
from gamestonk_terminal.helper_classes import ModelsNamespace as _models

# flake8: noqa
# pylint: disable=unused-import

# Menu commands
from gamestonk_terminal.common.technical_analysis.overlap_view import view_ma as ma
from gamestonk_terminal.common.technical_analysis.momentum_view import (
    display_cci as cci,
)
from gamestonk_terminal.common.technical_analysis.momentum_view import (
    display_macd as macd,
)
from gamestonk_terminal.common.technical_analysis.momentum_view import (
    display_rsi as rsi,
)
from gamestonk_terminal.common.technical_analysis.momentum_view import (
    display_stoch as stoch,
)
from gamestonk_terminal.common.technical_analysis.momentum_view import (
    display_fisher as fisher,
)
from gamestonk_terminal.common.technical_analysis.momentum_view import display_cg as cg
from gamestonk_terminal.common.technical_analysis.trend_indicators_view import (
    display_adx as adx,
)
from gamestonk_terminal.common.technical_analysis.trend_indicators_view import (
    display_aroon as aroon,
)
from gamestonk_terminal.common.technical_analysis.volatility_view import (
    display_bbands as bbands,
)
from gamestonk_terminal.common.technical_analysis.volatility_view import (
    display_donchian as donchian,
)
from gamestonk_terminal.common.technical_analysis.custom_indicators_view import (
    fibonacci_retracement as fib,
)

# Models
models = _models(os.path.abspath(os.path.dirname(__file__)))
