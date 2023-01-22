""" ECB view """
__docformat__ = "numpy"

from typing import Optional, List
from itertools import cycle
import logging
import os

from matplotlib import pyplot as plt

from openbb_terminal.config_terminal import theme
from openbb_terminal.config_plot import PLOT_DPI
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    export_data,
    plot_autoscale,
    is_valid_axes_count,
)
from openbb_terminal.fixedincome.ecb_model import get_series_data

logger = logging.getLogger(__name__)

ID_TO_NAME = {
    "EST.B.EU000A2X2A25.WT": "Euro Short-Term Rate: Volume-Weighted Trimmed Mean Rate [Percent]",
    "EST.B.EU000A2X2A25.TT": "Euro Short-Term Rate: Total Volume [Millions of EUR]",
    "EST.B.EU000A2X2A25.NT": "Euro Short-Term Rate: Number of Transactions",
    "EST.B.EU000A2X2A25.R75": "Euro Short-Term Rate: Rate at 75th Percentile of Volume [Percent]",
    "EST.B.EU000A2X2A25.NB": "Euro Short-Term Rate: Number of Active Banks",
    "EST.B.EU000A2X2A25.VL": "Euro Short-Term Rate: Share of Volume of the 5 Largest Active Banks [Percent]",
    "EST.B.EU000A2X2A25.R25": "Euro Short-Term Rate: Rate at 25th Percentile of Volume [Percent]",
}


@log_start_end(log=logger)
def plot_estr(
    series_id: str = "EST.B.EU000A2X2A25.WT",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Plot Euro Short-Term Rate (ESTR)

    Parameters
    ----------
    series_id: str
        ECB ID of ESTR data to plot, options: ['EST.B.EU000A2X2A25.WT', 'EST.B.EU000A2X2A25.TT', 'EST.B.EU000A2X2A25.NT', 'EST.B.EU000A2X2A25.R75', 'EST.B.EU000A2X2A25.NB', 'EST.B.EU000A2X2A25.VL', 'EST.B.EU000A2X2A25.R25']
    start_date: Optional[str]
        Start date, formatted YYYY-MM-DD
    end_date: Optional[str]
        End date, formatted YYYY-MM-DD
    export: str
        Export data to csv or excel file
    external_axes: Optional[List[plt.Axes]]
        External axes (1 axis is expected in the list)
    """
    df = get_series_data(
        series_id, start_date if start_date else "", end_date if end_date else ""
    )

    # This plot has 1 axis
    if not external_axes:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    elif is_valid_axes_count(external_axes, 1):
        (ax,) = external_axes
    else:
        return

    colors = cycle(theme.get_colors())
    ax.plot(
        df.index,
        df.values,
        marker="o",
        linestyle="dashed",
        linewidth=2,
        markersize=4,
        color=next(colors, "#FCED00"),
    )
    ax.set_title(ID_TO_NAME[series_id])
    theme.style_primary_axis(ax)

    if external_axes is None:
        theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        f"estr, {series_id}",
        df,
    )
