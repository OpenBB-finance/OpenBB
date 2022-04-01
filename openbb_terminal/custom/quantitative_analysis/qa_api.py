"""Pred context API."""

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
    display_cusum as cumsum,
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
