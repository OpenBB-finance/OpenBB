"""Technical Analysis API."""
import os
from openbb_terminal.helper_classes import ModelsNamespace as _models
from openbb_terminal.common import technical_analysis

# flake8: noqa
# pylint: disable=unused-import

# Menu commands
from openbb_terminal.common.technical_analysis.overlap_view import view_ma as ma
from openbb_terminal.common.technical_analysis.overlap_view import view_vwap as vwap
from openbb_terminal.common.technical_analysis.momentum_view import (
    display_cci as cci,
)
from openbb_terminal.common.technical_analysis.momentum_view import (
    display_macd as macd,
)
from openbb_terminal.common.technical_analysis.momentum_view import (
    display_rsi as rsi,
)
from openbb_terminal.common.technical_analysis.momentum_view import (
    display_stoch as stoch,
)
from openbb_terminal.common.technical_analysis.momentum_view import (
    display_fisher as fisher,
)
from openbb_terminal.common.technical_analysis.momentum_view import display_cg as cg
from openbb_terminal.common.technical_analysis.trend_indicators_view import (
    display_adx as adx,
)
from openbb_terminal.common.technical_analysis.trend_indicators_view import (
    display_aroon as aroon,
)
from openbb_terminal.common.technical_analysis.volatility_view import (
    display_bbands as bbands,
)
from openbb_terminal.common.technical_analysis.volatility_view import (
    display_donchian as donchian,
)
from openbb_terminal.common.technical_analysis.volatility_view import view_kc as kc
from openbb_terminal.common.technical_analysis.volume_view import display_ad as ad
from openbb_terminal.common.technical_analysis.volume_view import (
    display_adosc as adosc,
)
from openbb_terminal.common.technical_analysis.volume_view import display_obv as obv
from openbb_terminal.common.technical_analysis.custom_indicators_view import (
    fibonacci_retracement as fib,
)
from .finviz_view import view
from .finbrain_view import technical_summary_report as summary
from .tradingview_view import print_recommendation as recom


# Models
models = _models(
    [
        os.path.abspath(os.path.dirname(technical_analysis.__file__)),
        os.path.abspath(os.path.dirname(__file__)),
    ]
)
