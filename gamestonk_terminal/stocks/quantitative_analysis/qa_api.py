"""Quantitative Analysis API."""
import os
from gamestonk_terminal.helper_classes import ModelsNamespace as _models

# flake8: noqa
# pylint: disable=unused-import

# Menu commands
from gamestonk_terminal.common.quantitative_analysis.qa_view import display_raw as raw
from gamestonk_terminal.common.quantitative_analysis.qa_view import (
    display_summary as summary,
)
from gamestonk_terminal.common.quantitative_analysis.qa_view import display_line as line
from gamestonk_terminal.common.quantitative_analysis.qa_view import display_hist as hist
from gamestonk_terminal.common.quantitative_analysis.qa_view import display_cdf as cdf
from gamestonk_terminal.common.quantitative_analysis.qa_view import display_bw as bw
from gamestonk_terminal.common.quantitative_analysis.qa_view import (
    display_seasonal as decompose,
)
from gamestonk_terminal.common.quantitative_analysis.qa_view import (
    display_cusum as cusum,
)
from gamestonk_terminal.common.quantitative_analysis.qa_view import display_acf as acf
from gamestonk_terminal.common.quantitative_analysis.rolling_view import (
    display_mean_std as rolling,
)
from gamestonk_terminal.common.quantitative_analysis.rolling_view import (
    display_spread as spread,
)
from gamestonk_terminal.common.quantitative_analysis.rolling_view import (
    display_quantile as quantile,
)
from gamestonk_terminal.common.quantitative_analysis.rolling_view import (
    display_skew as skew,
)
from gamestonk_terminal.common.quantitative_analysis.rolling_view import (
    display_kurtosis as kurtosis,
)
from gamestonk_terminal.common.quantitative_analysis.qa_view import (
    display_normality as normality,
)
from gamestonk_terminal.common.quantitative_analysis.qa_view import (
    display_qqplot as qqplot,
)
from gamestonk_terminal.common.quantitative_analysis.qa_view import (
    display_unitroot as unitroot,
)
from .factors_view import capm_view as capm

# Models
# NOTE: The raw function is used here to point to the commons path where all the
#       qa models are expected to live
models = _models(
    [
        os.path.abspath(os.path.dirname(raw.__code__.co_filename)),
        os.path.abspath(os.path.dirname(__file__)),
    ]
)
