"""Quantitative Analysis API."""
import os
from openbb_terminal.helper_classes import ModelsNamespace as _models

# flake8: noqa
# pylint: disable=unused-import

# Menu commands
from openbb_terminal.common.quantitative_analysis.qa_view import display_raw as raw
from openbb_terminal.common.quantitative_analysis.qa_view import (
    display_summary as summary,
)
from openbb_terminal.common.quantitative_analysis.qa_view import display_line as line
from openbb_terminal.common.quantitative_analysis.qa_view import display_hist as hist
from openbb_terminal.common.quantitative_analysis.qa_view import display_cdf as cdf
from openbb_terminal.common.quantitative_analysis.qa_view import display_bw as bw
from openbb_terminal.common.quantitative_analysis.qa_view import (
    display_seasonal as decompose,
)
from openbb_terminal.common.quantitative_analysis.qa_view import (
    display_cusum as cusum,
)
from openbb_terminal.common.quantitative_analysis.qa_view import display_acf as acf
from openbb_terminal.common.quantitative_analysis.rolling_view import (
    display_mean_std as rolling,
)
from openbb_terminal.common.quantitative_analysis.rolling_view import (
    display_spread as spread,
)
from openbb_terminal.common.quantitative_analysis.rolling_view import (
    display_quantile as quantile,
)
from openbb_terminal.common.quantitative_analysis.rolling_view import (
    display_skew as skew,
)
from openbb_terminal.common.quantitative_analysis.rolling_view import (
    display_kurtosis as kurtosis,
)
from openbb_terminal.common.quantitative_analysis.qa_view import (
    display_normality as normality,
)
from openbb_terminal.common.quantitative_analysis.qa_view import (
    display_qqplot as qqplot,
)
from openbb_terminal.common.quantitative_analysis.qa_view import (
    display_unitroot as unitroot,
)

# Models
# NOTE: The raw function is used here to point to the commons path where all the
#       qa models are expected to live
models = _models(
    [
        os.path.abspath(os.path.dirname(raw.__code__.co_filename)),
        os.path.abspath(os.path.dirname(__file__)),
    ]
)
