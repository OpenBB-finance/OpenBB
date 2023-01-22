""" NYFED view """
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
from openbb_terminal.fixedincome import nyfed_model

logger = logging.getLogger(__name__)

SERIES_TO_NAME_SOFR = {
    "overnight": "Secured Overnight Financing Rate (SOFR) [Percent]",
    "30_day": "30-Day Average SOFR [Percent]",
    "90_day": "90-Day Average SOFR [Percent]",
    "180_day": "180-Day Average SOFR [Percent]",
    "index": "SOFR Index",
}
SERIES_TO_NAME_EFFR = {
    "percentRate": "Effective Federal Funds Rate [Percent]",
    "volumeInBillions": "Effective Federal Funds Volume [Billions of USD]",
    "percentPercentile1": "Effective Federal Funds Rate: 1th Percentile [Percent]",
    "percentPercentile25": "Effective Federal Funds Rate: 25th Percentile [Percent]",
    "percentPercentile75": "Effective Federal Funds Rate: 75th Percentile [Percent]",
    "percentPercentile99": "Effective Federal Funds Rate: 99th Percentile [Percent]",
}
SERIES_TO_NAME_OBFR = {
    "percentRate": "Overnight Bank Funding Rate [Percent]",
    "volumeInBillions": "Overnight Bank Funding Volume [Billions of USD]",
    "percentPercentile1": "Overnight Bank Funding Rate: 1th Percentile [Percent]",
    "percentPercentile25": "Overnight Bank Funding Rate: 25th Percentile [Percent]",
    "percentPercentile75": "Overnight Bank Funding Rate: 75th Percentile [Percent]",
    "percentPercentile99": "Overnight Bank Funding Rate: 99th Percentile [Percent]",
}


@log_start_end(log=logger)
def plot_sofr(
    series: str = "overnight",
    start_date: Optional[str] = "1980-01-01",
    end_date: Optional[str] = None,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Plot Secured Overnight Financing Rate (SOFR)

    Parameters
    ----------
    series: str
        Specific data to plot, options: ['overnight', '30_day', '90_day', '180_day', 'index']
    start_date: Optional[str]
        Start date, formatted YYYY-MM-DD
    end_date: Optional[str]
        End date, formatted YYYY-MM-DD
    export: str
        Export data to csv or excel file
    external_axes: Optional[List[plt.Axes]]
        External axes (1 axis is expected in the list)
    """
    df = nyfed_model.get_sofr_data(series, start_date, end_date if end_date else "")
    if series == "overnight":
        del df["volumeInBillions"]

    # This plot has 1 axis
    if not external_axes:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    elif is_valid_axes_count(external_axes, 1):
        (ax,) = external_axes
    else:
        return

    ax.plot(
        df.index,
        df.values,
        marker="o",
        linestyle="dashed",
        linewidth=2,
        markersize=4,
    )
    ax.set_title(SERIES_TO_NAME_SOFR[series])
    theme.style_primary_axis(ax)

    if series.lower() == "overnight":
        ax.legend(
            [
                "Rate",
                "1th percentile",
                "25th percentile",
                "75th percentile",
                "99th percentile",
            ]
        )

    if external_axes is None:
        theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        f"sofr, {series}",
        df,
    )


@log_start_end(log=logger)
def plot_fftr(
    start_date: Optional[str] = "1980-01-01",
    end_date: Optional[str] = None,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Plot Federal Funding Target Range (upper and lower)

    Parameters
    ----------
    start_date: Optional[str]
        Start date, formatted YYYY-MM-DD
    end_date: Optional[str]
        End date, formatted YYYY-MM-DD
    export: str
        Export data to csv or excel file
    external_axes: Optional[List[plt.Axes]]
        External axes (1 axis is expected in the list)
    """
    df = nyfed_model.get_effr_data(start_date, end_date if end_date else "")
    df = df[["targetRateTo", "targetRateFrom"]]

    # This plot has 1 axis
    if not external_axes:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    elif is_valid_axes_count(external_axes, 1):
        (ax,) = external_axes
    else:
        return

    ax.plot(
        df.index,
        df.values,
        marker="o",
        linestyle="dashed",
        linewidth=2,
        markersize=4,
    )
    ax.set_title("Federal Funds Target Range [Percent]")
    ax.legend(["Upper limit", "Lower limit"])
    theme.style_primary_axis(ax)

    if external_axes is None:
        theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        f"fftr",
        df,
    )


@log_start_end(log=logger)
def plot_effr(
    series: str = "percentRate",
    start_date: Optional[str] = "1980-01-01",
    end_date: Optional[str] = None,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Plot Effective Federal Funds Rate

    Parameters
    ----------
    series: str
        Specific data to plot, options: ['percentRate', 'volumeInBillions', 'percentPercentile1', 'percentPercentile25', 'percentPercentile75', 'percentPercentile99']
    start_date: Optional[str]
        Start date, formatted YYYY-MM-DD
    end_date: Optional[str]
        End date, formatted YYYY-MM-DD
    export: str
        Export data to csv or excel file
    external_axes: Optional[List[plt.Axes]]
        External axes (1 axis is expected in the list)
    """
    df = nyfed_model.get_effr_data(start_date, end_date if end_date else "")
    df = df[series]

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
    ax.set_title(SERIES_TO_NAME_EFFR[series])
    theme.style_primary_axis(ax)

    if external_axes is None:
        theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        f"effr, {series}",
        df,
    )


@log_start_end(log=logger)
def plot_obfr(
    series: str = "percentRate",
    start_date: Optional[str] = "1980-01-01",
    end_date: Optional[str] = None,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Plot Overnight Bank Funding Rate

    Parameters
    ----------
    series: str
        Specific data to plot, options: ['percentRate', 'volumeInBillions', 'percentPercentile1', 'percentPercentile25', 'percentPercentile75', 'percentPercentile99']
    start_date: Optional[str]
        Start date, formatted YYYY-MM-DD
    end_date: Optional[str]
        End date, formatted YYYY-MM-DD
    export: str
        Export data to csv or excel file
    external_axes: Optional[List[plt.Axes]]
        External axes (1 axis is expected in the list)
    """
    df = nyfed_model.get_obfr_data(start_date, end_date if end_date else "")
    df = df[series]

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
    ax.set_title(SERIES_TO_NAME_OBFR[series])
    theme.style_primary_axis(ax)

    if external_axes is None:
        theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        f"obfr, {series}",
        df,
    )
