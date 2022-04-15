"""Quantitative Analysis View"""
__docformat__ = "numpy"

# pylint: disable=too-many-lines


import logging
import os
import warnings
from datetime import datetime
from typing import Any, Optional, List

import matplotlib
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
import seaborn as sns
import statsmodels.api as sm
from scipy import stats
from detecta import detect_cusum
from statsmodels.graphics.gofplots import qqplot
from pandas.plotting import register_matplotlib_converters

from openbb_terminal.config_terminal import theme
from openbb_terminal.common.quantitative_analysis import qa_model
from openbb_terminal.config_plot import PLOT_DPI
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_classes import LineAnnotateDrawer
from openbb_terminal.helper_funcs import (
    export_data,
    plot_autoscale,
    print_rich_table,
    reindex_dates,
    lambda_long_number_format,
)
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)

register_matplotlib_converters()

# TODO : Since these are common/ they should be independent of 'stock' info.
# df_stock should be replaced with a generic df and a column variable


def lambda_color_red(val: Any) -> str:
    """Adds red to dataframe value"""
    if val > 0.05:
        return f"[red]{round(val,4)}[/red]"
    return round(val, 4)


@log_start_end(log=logger)
def display_summary(df: pd.DataFrame, export: str):
    """Show summary statistics

    Parameters
    ----------
    df_stock : pd.DataFrame
        DataFrame to get statistics of
    export : str
        Format to export data
    """
    summary = qa_model.get_summary(df)

    print_rich_table(
        summary,
        headers=list(summary.columns),
        floatfmt=".3f",
        show_index=True,
        title="[bold]Summary Statistics[/bold]",
    )
    console.print("")
    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        "summary",
        summary,
    )


@log_start_end(log=logger)
def display_hist(
    name: str,
    df: pd.DataFrame,
    target: str,
    bins: int,
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Generate of histogram of data

    Parameters
    ----------
    name : str
        Name of dataset
    df : pd.DataFrame
        Dataframe to look at
    target : str
        Data column to get histogram of the dataframe
    bins : int
        Number of bins in histogram
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """
    data = df[target]

    # This plot has 1 axis
    if external_axes is None:
        _, ax = plt.subplots(
            figsize=plot_autoscale(),
            dpi=PLOT_DPI,
        )
    else:
        if len(external_axes) != 1:
            logger.error("Expected list of one axis item.")
            console.print("[red]Expected list of 1 axis items./n[/red]")
            return
        (ax,) = external_axes

    sns.histplot(
        data,
        color=theme.up_color,
        bins=bins,
        kde=True,
        ax=ax,
        stat="proportion",
        legend=True,
    )
    sns.rugplot(data, color=theme.down_color, ax=ax, legend=True)

    if isinstance(df.index[0], datetime):
        start = df.index[0]
        ax.set_title(f"Histogram of {name} {target} from {start.strftime('%Y-%m-%d')}")
    else:
        ax.set_title(f"Histogram of {name} {target}")

    ax.set_xlabel("Value")
    theme.style_primary_axis(ax)

    # Manually construct the chart legend
    proportion_legend = mpatches.Patch(
        color=theme.up_color, label="Univariate distribution"
    )
    marginal_legend = mpatches.Patch(
        color=theme.down_color, label="Marginal distributions"
    )
    ax.legend(handles=[proportion_legend, marginal_legend])

    if external_axes is None:
        theme.visualize_output()


@log_start_end(log=logger)
def display_cdf(
    name: str,
    df: pd.DataFrame,
    target: str,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Plot Cumulative Distribution Function

    Parameters
    ----------
    name : str
        Name of dataset
    df : pd.DataFrame
        Dataframe to look at
    target : str
        Data column
    export : str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """
    data = df[target]
    start = df.index[0]
    cdf = data.value_counts().sort_index().div(len(data)).cumsum()

    # This plot has 1 axis
    if external_axes is None:
        _, ax = plt.subplots(
            figsize=plot_autoscale(),
            dpi=PLOT_DPI,
        )
    else:
        if len(external_axes) != 1:
            logger.error("Expected list of one axis item.")
            console.print("[red]Expected list of 1 axis items./n[/red]")
            return
        (ax,) = external_axes

    cdf.plot(ax=ax)
    ax.set_title(
        f"Cumulative Distribution Function of {name} {target}\nfrom {start.strftime('%Y-%m-%d')}"
    )
    ax.set_ylabel("Probability")
    ax.set_xlabel(target)

    minVal = data.values.min()
    q25 = np.quantile(data.values, 0.25)
    medianVal = np.quantile(data.values, 0.5)
    q75 = np.quantile(data.values, 0.75)
    labels = [
        (minVal, q25),
        (0.25, 0.25),
        theme.down_color,
        (q25, q25),
        (0, 0.25),
        theme.down_color,
        (minVal, medianVal),
        (0.5, 0.5),
        theme.down_color,
        (medianVal, medianVal),
        (0, 0.5),
        theme.down_color,
        (minVal, q75),
        (0.75, 0.75),
        theme.down_color,
        (q75, q75),
        (0, 0.75),
        theme.down_color,
    ]
    ax.plot(*labels, ls="--")
    ax.text(
        minVal + (q25 - minVal) / 2,
        0.27,
        "Q1",
        color=theme.down_color,
        fontweight="bold",
    )
    ax.text(
        minVal + (medianVal - minVal) / 2,
        0.52,
        "Median",
        color=theme.down_color,
        fontweight="bold",
    )
    ax.text(
        minVal + (q75 - minVal) / 2,
        0.77,
        "Q3",
        color=theme.down_color,
        fontweight="bold",
    )
    ax.set_xlim(cdf.index[0], cdf.index[-1])
    theme.style_primary_axis(ax)

    if external_axes is None:
        theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        "cdf",
        pd.DataFrame(cdf),
    )


@log_start_end(log=logger)
def display_bw(
    name: str,
    df: pd.DataFrame,
    target: str,
    yearly: bool,
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Show box and whisker plots

    Parameters
    ----------
    name : str
        Name of dataset
    df : pd.DataFrame
        Dataframe to look at
    target : str
        Data column to look at
    yearly : bool
        Flag to indicate yearly accumulation
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """
    data = df[target]
    start = df.index[0]

    # This plot has 1 axis
    if external_axes is None:
        _, ax = plt.subplots(
            figsize=plot_autoscale(),
            dpi=PLOT_DPI,
        )
    else:
        if len(external_axes) != 1:
            logger.error("Expected list of one axis item.")
            console.print("[red]Expected list of 1 axis items./n[/red]")
            return
        (ax,) = external_axes

    color = theme.get_colors()[0]
    if yearly:
        x_data = data.index.year
    else:
        x_data = data.index.month
    box_plot = sns.boxplot(
        x=x_data,
        y=data,
        ax=ax,
        zorder=3,
        boxprops=dict(edgecolor=color),
        flierprops=dict(
            linestyle="--",
            color=color,
            markerfacecolor=theme.up_color,
            markeredgecolor=theme.up_color,
        ),
        whiskerprops=dict(color=color),
        capprops=dict(color=color),
    )

    box_plot.set(
        xlabel=["Monthly", "Yearly"][yearly],
        ylabel=target,
        title=f"{['Monthly','Yearly'][yearly]} box plot of {name} {target} from {start.strftime('%Y-%m-%d')}",
    )
    l_months = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ]
    l_ticks = list()
    if not yearly:
        for val in box_plot.get_xticklabels():
            l_ticks.append(l_months[int(val.get_text()) - 1])
        box_plot.set_xticklabels(l_ticks)

    # remove the scientific notion on the left hand side
    ax.ticklabel_format(style="plain", axis="y")
    ax.get_yaxis().set_major_formatter(
        matplotlib.ticker.FuncFormatter(lambda x, _: lambda_long_number_format(x))
    )

    theme.style_primary_axis(ax)

    if external_axes is None:
        theme.visualize_output()


@log_start_end(log=logger)
def display_acf(
    name: str,
    df: pd.DataFrame,
    target: str,
    lags: int,
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Show Auto and Partial Auto Correlation of returns and change in returns

    Parameters
    ----------
    name : str
        Name of dataset
    df : pd.DataFrame
        Dataframe to look at
    target : str
        Data column to look at
    lags : int
        Max number of lags to look at
    external_axes : Optional[List[plt.Axes]], optional
        External axes (4 axes are expected in the list), by default None
    """
    df = df[target]
    start = df.index[0]

    # This plot has 4 axes
    if external_axes is None:
        fig, axes = plt.subplots(
            nrows=2,
            ncols=2,
            figsize=plot_autoscale(),
            dpi=PLOT_DPI,
        )
        (ax1, ax2), (ax3, ax4) = axes
    else:
        if len(external_axes) != 4:
            logger.error("Expected list of four axis items.")
            console.print("[red]Expected list of 4 axis items./n[/red]")
            return
        (ax1, ax2, ax3, ax4) = external_axes

    # Diff Auto-correlation function for original time series
    sm.graphics.tsa.plot_acf(np.diff(np.diff(df.values)), lags=lags, ax=ax1)
    ax1.set_title(f"{name} Returns Auto-Correlation", fontsize=9)
    # Diff Partial auto-correlation function for original time series
    sm.graphics.tsa.plot_pacf(np.diff(np.diff(df.values)), lags=lags, ax=ax2)
    ax2.set_title(
        f"{name} Returns Partial Auto-Correlation",
        fontsize=9,
    )

    # Diff Diff Auto-correlation function for original time series
    sm.graphics.tsa.plot_acf(np.diff(np.diff(df.values)), lags=lags, ax=ax3)
    ax3.set_title(
        f"Change in {name} Returns Auto-Correlation",
        fontsize=9,
    )
    # Diff Diff Partial auto-correlation function for original time series
    sm.graphics.tsa.plot_pacf(np.diff(np.diff(df.values)), lags=lags, ax=ax4)
    ax4.set_title(
        f"Change in {name} Returns Partial Auto-Correlation",
        fontsize=9,
    )

    fig.suptitle(
        f"ACF differentials starting from {start.strftime('%Y-%m-%d')}",
        fontsize=15,
        x=0.042,
        y=0.95,
        horizontalalignment="left",
        verticalalignment="top",
    )
    theme.style_primary_axis(ax1)
    theme.style_primary_axis(ax2)
    theme.style_primary_axis(ax3)
    theme.style_primary_axis(ax4)

    if external_axes is None:
        theme.visualize_output(force_tight_layout=True)


@log_start_end(log=logger)
def display_qqplot(
    name: str,
    df: pd.DataFrame,
    target: str,
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Show QQ plot for data against normal quantiles

    Parameters
    ----------
    name : str
        Stock ticker
    df : pd.DataFrame
        Dataframe
    target : str
        Column in data to look at
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """
    # Statsmodels has a UserWarning for marker kwarg-- which we don't use
    warnings.filterwarnings(category=UserWarning, action="ignore")
    data = df[target]

    # This plot has 1 axis
    if external_axes is None:
        _, ax = plt.subplots(
            figsize=plot_autoscale(),
            dpi=PLOT_DPI,
        )
    else:
        if len(external_axes) != 1:
            logger.error("Expected list of one axis item.")
            console.print("[red]Expected list of 1 axis items./n[/red]")
            return
        (ax,) = external_axes

    qqplot(
        data,
        stats.distributions.norm,
        fit=True,
        line="45",
        color=theme.down_color,
        ax=ax,
    )
    ax.get_lines()[1].set_color(theme.up_color)

    ax.set_title(f"Q-Q plot for {name} {target}")
    ax.set_ylabel("Sample quantiles")
    ax.set_xlabel("Theoretical quantiles")

    theme.style_primary_axis(ax)

    if external_axes is None:
        theme.visualize_output()


@log_start_end(log=logger)
def display_cusum(
    df: pd.DataFrame,
    target: str,
    threshold: float,
    drift: float,
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Cumulative sum algorithm (CUSUM) to detect abrupt changes in data

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe
    target : str
        Column of data to look at
    threshold : float
        Threshold value
    drift : float
        Drift parameter
    external_axes : Optional[List[plt.Axes]], optional
        External axes (2 axes are expected in the list), by default None
    """
    target_series = df[target].values

    # The code for this plot was adapted from detecta's sources because at the
    # time of writing this detect_cusum had a bug related to external axes support.
    # see https://github.com/demotu/detecta/pull/3
    tap, tan = 0, 0
    ta, tai, taf, _ = detect_cusum(
        x=target_series,
        threshold=threshold,
        drift=drift,
        ending=True,
        show=False,
    )
    # Thus some variable names are left unchanged and unreadable...
    gp, gn = np.zeros(target_series.size), np.zeros(target_series.size)
    for i in range(1, target_series.size):
        s = target_series[i] - target_series[i - 1]
        gp[i] = gp[i - 1] + s - drift  # cumulative sum for + change
        gn[i] = gn[i - 1] - s - drift  # cumulative sum for - change
        if gp[i] < 0:
            gp[i], tap = 0, i
        if gn[i] < 0:
            gn[i], tan = 0, i
        if gp[i] > threshold or gn[i] > threshold:  # change detected!
            ta = np.append(ta, i)  # alarm index
            tai = np.append(tai, tap if gp[i] > threshold else tan)  # start
            gp[i], gn[i] = 0, 0  # reset alarm

    if external_axes is None:
        _, axes = plt.subplots(
            2,
            1,
            sharex=True,
            figsize=plot_autoscale(),
            dpi=PLOT_DPI,
        )
        (ax1, ax2) = axes
    else:
        if len(external_axes) != 2:
            logger.error("Expected list of two axis items.")
            console.print("[red]Expected list of 2 axis items./n[/red]")
            return
        (ax1, ax2) = external_axes

    target_series_indexes = range(df[target].size)
    ax1.plot(target_series_indexes, target_series)
    if len(ta):
        ax1.plot(
            tai,
            target_series[tai],
            ">",
            markerfacecolor=theme.up_color,
            markersize=5,
            label="Start",
        )
        ax1.plot(
            taf,
            target_series[taf],
            "<",
            markerfacecolor=theme.down_color,
            markersize=5,
            label="Ending",
        )
        ax1.plot(
            ta,
            target_series[ta],
            "o",
            markerfacecolor=theme.get_colors()[-1],
            markeredgecolor=theme.get_colors()[-2],
            markeredgewidth=1,
            markersize=3,
            label="Alarm",
        )
        ax1.legend()
    ax1.set_xlim(-0.01 * target_series.size, target_series.size * 1.01 - 1)
    ax1.set_ylabel("Amplitude")
    ymin, ymax = (
        target_series[np.isfinite(target_series)].min(),
        target_series[np.isfinite(target_series)].max(),
    )
    y_range = ymax - ymin if ymax > ymin else 1
    ax1.set_ylim(ymin - 0.1 * y_range, ymax + 0.1 * y_range)
    ax1.set_title(
        "Time series and detected changes "
        + f"(threshold= {threshold:.3g}, drift= {drift:.3g}): N changes = {len(tai)}",
        fontsize=10,
    )
    theme.style_primary_axis(ax1)

    ax2.plot(target_series_indexes, gp, label="+")
    ax2.plot(target_series_indexes, gn, label="-")
    ax2.set_xlim(-0.01 * target_series.size, target_series.size * 1.01 - 1)
    ax2.set_xlabel("Data points")
    ax2.set_ylim(-0.01 * threshold, 1.1 * threshold)
    ax2.axhline(threshold)
    theme.style_primary_axis(ax2)

    ax2.set_title(
        "Time series of the cumulative sums of positive and negative changes",
        fontsize=10,
    )
    ax2.legend()

    if external_axes is None:
        theme.visualize_output()


@log_start_end(log=logger)
def display_seasonal(
    name: str,
    df: pd.DataFrame,
    target: str,
    multiplicative: bool = False,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Display seasonal decomposition data

    Parameters
    ----------
    name : str
        Name of dataset
    df : pd.DataFrame
        DataFrame
    target : str
        Column of data to look at
    multiplicative : bool
        Boolean to indicate multiplication instead of addition
    export : str
        Format to export trend and cycle df
    external_axes : Optional[List[plt.Axes]], optional
        External axes (6 axes are expected in the list), by default None
    """
    data = df[target]
    result, cycle, trend = qa_model.get_seasonal_decomposition(data, multiplicative)

    plot_data = pd.merge(
        data,
        result.trend,
        how="outer",
        left_index=True,
        right_index=True,
        suffixes=("", "_result.trend"),
    )
    plot_data = pd.merge(
        plot_data,
        result.seasonal,
        how="outer",
        left_index=True,
        right_index=True,
        suffixes=("", "_result.seasonal"),
    )
    plot_data = pd.merge(
        plot_data,
        result.resid,
        how="outer",
        left_index=True,
        right_index=True,
        suffixes=("", "_result.resid"),
    )
    plot_data = pd.merge(
        plot_data,
        cycle,
        how="outer",
        left_index=True,
        right_index=True,
        suffixes=("", "_cycle"),
    )
    plot_data = pd.merge(
        plot_data,
        trend,
        how="outer",
        left_index=True,
        right_index=True,
        suffixes=("", "_trend"),
    )
    plot_data = reindex_dates(plot_data)

    # This plot has 1 axis
    if external_axes is None:
        fig, axes = plt.subplots(
            4,
            1,
            sharex=True,
            figsize=plot_autoscale(),
            dpi=PLOT_DPI,
        )
        (ax1, ax2, ax3, ax4) = axes
    else:
        if len(external_axes) != 4:
            logger.error("Expected list of four axis items.")
            console.print("[red]Expected list of 4 axis items./n[/red]")
            return
        (ax1, ax2, ax3, ax4) = external_axes

    colors = iter(theme.get_colors())

    ax1.set_title(f"{name} (Time-Series) {target} seasonal decomposition")
    ax1.plot(
        plot_data.index, plot_data[target].values, color=next(colors), label="Values"
    )
    ax1.set_xlim([plot_data.index[0], plot_data.index[-1]])
    ax1.legend()

    # Multiplicative model
    ax2.plot(plot_data["trend"], color=theme.down_color, label="Cyclic-Trend")
    ax2.plot(
        plot_data["trend_cycle"],
        color=theme.up_color,
        linestyle="--",
        label="Cycle component",
    )
    ax2.legend()

    ax3.plot(plot_data["trend_trend"], color=next(colors), label="Trend component")
    ax3.plot(plot_data["seasonal"], color=next(colors), label="Seasonal effect")
    ax3.legend()

    ax4.plot(plot_data["resid"], color=next(colors), label="Residuals")
    ax4.legend()

    theme.style_primary_axis(ax1)
    theme.style_primary_axis(ax2)
    theme.style_primary_axis(ax3)
    theme.style_primary_axis(
        ax4,
        data_index=plot_data.index.to_list(),
        tick_labels=plot_data["date"].to_list(),
    )

    if external_axes is None:
        fig.tight_layout(pad=theme.tight_layout_padding)
        fig.subplots_adjust(
            hspace=0.1,
        )
        theme.visualize_output(force_tight_layout=False)

    # From  # https://otexts.com/fpp2/seasonal-strength.html
    console.print("Time-Series Level is " + str(round(data.mean(), 2)))

    Ft = max(0, 1 - np.var(result.resid)) / np.var(result.trend + result.resid)
    console.print(f"Strength of Trend: {Ft:.4f}")

    Fs = max(
        0,
        1 - np.var(result.resid) / np.var(result.seasonal + result.resid),
    )
    console.print(f"Strength of Seasonality: {Fs:.4f}\n")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        "summary",
        cycle.join(trend),
    )


@log_start_end(log=logger)
def display_normality(df: pd.DataFrame, target: str, export: str = ""):
    """View normality statistics

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame
    target : str
        Column in data to look at
    export : str
        Format to export data
    """
    data = df[target]
    normal = qa_model.get_normality(data)
    stats1 = normal.copy().T
    stats1.iloc[:, 1] = stats1.iloc[:, 1].apply(lambda x: lambda_color_red(x))

    print_rich_table(
        stats1,
        show_index=True,
        headers=["Statistic", "p-value"],
        floatfmt=".4f",
        title="[bold]Normality Statistics[/bold]",
    )
    console.print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        "normality",
        normal,
    )


@log_start_end(log=logger)
def display_unitroot(
    df: pd.DataFrame, target: str, fuller_reg: str, kpss_reg: str, export: str = ""
):
    """Show unit root test calculations

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame
    target : str
        Column of data to look at
    fuller_reg : str
        Type of regression of ADF test
    kpss_reg : str
        Type of regression for KPSS test
    export : str
        Format for exporting data
    """
    df = df[target]
    data = qa_model.get_unitroot(df, fuller_reg, kpss_reg)
    print_rich_table(
        data,
        show_index=True,
        headers=list(data.columns),
        title="[bold]Unit Root Calculation[/bold]",
        floatfmt=".4f",
    )
    console.print("")
    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        "unitroot",
        data,
    )


@log_start_end(log=logger)
def display_raw(
    df: pd.DataFrame, sort: str = "", des: bool = False, num: int = 20, export: str = ""
) -> None:
    """Return raw stock data

    Parameters
    ----------
    df : DataFrame
        DataFrame with historical information
    sort : str
        The column to sort by
    des : bool
        Whether to sort descending
    num : int
        Number of rows to show
    export : str
        Export data as CSV, JSON, XLSX
    """

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "history",
        df,
    )

    if isinstance(df, pd.Series):
        df1 = pd.DataFrame(df)
    else:
        df1 = df.copy()

    if sort:
        df1 = df.sort_values(by=sort, ascending=des)
    df1.index = [x.strftime("%Y-%m-%d") for x in df.index]
    print_rich_table(
        df1.tail(num),
        headers=[x.title() if x != "" else "Date" for x in df1.columns],
        title="[bold]Raw Data[/bold]",
        show_index=True,
        floatfmt=".3f",
    )

    console.print("")


@log_start_end(log=logger)
def display_line(
    data: pd.Series,
    title: str = "",
    log_y: bool = True,
    draw: bool = False,
    markers_lines: Optional[List[datetime]] = None,
    markers_scatter: Optional[List[datetime]] = None,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Display line plot of data

    Parameters
    ----------
    data: pd.Series
        Data to plot
    title: str
        Title for plot
    log_y: bool
        Flag for showing y on log scale
    draw: bool
        Flag for drawing lines and annotating on the plot
    markers_lines: Optional[List[datetime]]
        List of dates to highlight using vertical lines
    markers_scatter: Optional[List[datetime]]
        List of dates to highlight using scatter
    export: str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """
    # This plot has 1 axis
    if external_axes is None:
        _, ax = plt.subplots(
            figsize=plot_autoscale(),
            dpi=PLOT_DPI,
        )
    else:
        if len(external_axes) != 1:
            logger.error("Expected list of one axis item.")
            console.print("[red]Expected list of 1 axis items./n[/red]")
            return
        (ax,) = external_axes

    if log_y:
        ax.semilogy(data.index, data.values)
        ax.yaxis.set_major_formatter(matplotlib.ticker.ScalarFormatter())
        ax.yaxis.set_major_locator(
            matplotlib.ticker.LogLocator(base=100, subs=[1.0, 2.0, 5.0, 10.0])
        )
        ax.ticklabel_format(style="plain", axis="y")

    else:
        ax.plot(data.index, data.values)

        if markers_lines:
            ymin, ymax = ax.get_ylim()
            ax.vlines(markers_lines, ymin, ymax, color="#00AAFF")

        if markers_scatter:
            for n, marker_date in enumerate(markers_scatter):
                price_location_idx = data.index.get_loc(marker_date, method="nearest")
                # algo to improve text placement of highlight event number
                if (
                    0 < price_location_idx < (len(data) - 1)
                    and data.iloc[price_location_idx - 1]
                    > data.iloc[price_location_idx]
                    and data.iloc[price_location_idx + 1]
                    > data.iloc[price_location_idx]
                ):
                    text_loc = (0, -20)
                else:
                    text_loc = (0, 10)
                ax.annotate(
                    str(n + 1),
                    (mdates.date2num(marker_date), data.iloc[price_location_idx]),
                    xytext=text_loc,
                    textcoords="offset points",
                )
                ax.scatter(
                    marker_date,
                    data.iloc[price_location_idx],
                    color="#00AAFF",
                    s=100,
                )

    data_type = data.name
    ax.set_ylabel(data_type)
    ax.set_xlim(data.index[0], data.index[-1])
    ax.ticklabel_format(style="plain", axis="y")
    ax.get_yaxis().set_major_formatter(
        matplotlib.ticker.FuncFormatter(lambda x, _: lambda_long_number_format(x))
    )

    if title:
        ax.set_title(title)
    if draw:
        LineAnnotateDrawer(ax).draw_lines_and_annotate()

    theme.style_primary_axis(ax)

    if external_axes is None:
        theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        "line",
    )


def display_var(
    data: pd.DataFrame,
    ticker: str = "",
    use_mean: bool = False,
    adjusted_var: bool = False,
    student_t: bool = False,
    percentile: float = 0.999,
    portfolio: bool = False,
):
    """Displays VaR of dataframe

    Parameters
    ----------
    data: pd.Dataframe
        stock dataframe
    use_mean: bool
        if one should use the stocks mean return
    ticker: str
        ticker of the stock
    adjusted_var: bool
        if one should have VaR adjusted for skew and kurtosis (Cornish-Fisher-Expansion)
    student_t: bool
        If one should use the student-t distribution
    percentile: int
        var percentile
    portfolio: bool
        If the data is a portfolio
    """
    var_list, hist_var_list = qa_model.get_var(
        data, use_mean, adjusted_var, student_t, percentile, portfolio
    )

    str_hist_label = "Historical VaR:"

    if adjusted_var:
        str_var_label = "Adjusted VaR:"
        str_title = "Adjusted "
    elif student_t:
        str_var_label = "Student-t VaR"
        str_title = "Student-t "
    else:
        str_var_label = "VaR:"
        str_title = ""

    if ticker != "":
        ticker += " "

    data_dictionary = {str_var_label: var_list, str_hist_label: hist_var_list}
    data = pd.DataFrame(
        data_dictionary, index=["90.0%", "95.0%", "99.0%", f"{percentile*100}%"]
    )

    print_rich_table(
        data,
        show_index=True,
        headers=list(data.columns),
        title=f"[bold]{ticker}{str_title}Value at Risk[/bold]",
        floatfmt=".4f",
    )
    console.print("")


def display_es(
    data: pd.DataFrame,
    ticker: str = "",
    use_mean: bool = False,
    distribution: str = "normal",
    percentile: float = 0.999,
    portfolio: bool = False,
):
    """Displays expected shortfall

    Parameters
    ----------
    data: pd.DataFrame
        stock dataframe
    use_mean:
        if one should use the stocks mean return
    ticker: str
        ticker of the stock
    distribution: str
        choose distribution to use: logistic, laplace, normal
    percentile: int
        es percentile
    portfolio: bool
        If the data is a portfolio
    """
    es_list, hist_es_list = qa_model.get_es(
        data, use_mean, distribution, percentile, portfolio
    )

    str_hist_label = "Historical ES:"

    if distribution == "laplace":
        str_es_label = "Laplace ES:"
        str_title = "Laplace "
    elif distribution == "student_t":
        str_es_label = "Student-t ES"
        str_title = "Student-t "
    elif distribution == "logistic":
        str_es_label = "Logistic ES"
        str_title = "Logistic "
    else:
        str_es_label = "ES:"
        str_title = ""

    if ticker != "":
        ticker += " "

    data_dictionary = {str_es_label: es_list, str_hist_label: hist_es_list}
    data = pd.DataFrame(
        data_dictionary, index=["90.0%", "95.0%", "99.0%", f"{percentile*100}%"]
    )

    print_rich_table(
        data,
        show_index=True,
        headers=list(data.columns),
        title=f"[bold]{ticker}{str_title}Expected Shortfall[/bold]",
        floatfmt=".4f",
    )
    console.print("")


def display_sharpe(data: pd.DataFrame, rfr: float, window: float):
    """Calculates the sharpe ratio
    Parameters
    ----------
    data: pd.DataFrame
        selected dataframe column
    rfr: float
        risk free rate
    window: float
        length of the rolling window
    """
    sharpe_ratio = qa_model.get_sharpe(data, rfr, window)

    fig, ax = plt.subplots()
    ax.plot(sharpe_ratio[int(window - 1) :])
    ax.set_title(f"Sharpe Ratio - over a {window} day window")
    ax.set_ylabel("Sharpe ratio")
    ax.set_xlabel("Date")
    fig.legend()

    theme.style_primary_axis(ax)
    theme.visualize_output()


def display_sortino(
    data: pd.DataFrame, target_return: float, window: float, adjusted: bool
):
    """Displays the sortino ratio
    Parameters
    ----------
    data: pd.DataFrame
        selected dataframe
    target_return: float
        target return of the asset
    window: float
        length of the rolling window
    adjusted: bool
        adjust the sortino ratio
    """
    sortino_ratio = qa_model.get_sortino(data, target_return, window, adjusted)
    if adjusted:
        str_adjusted = "Adjusted "
    else:
        str_adjusted = ""

    fig, ax = plt.subplots()
    ax.plot(sortino_ratio[int(window - 1) :])
    ax.set_title(f"{str_adjusted}Sortino Ratio - over a {window} day window")
    ax.set_ylabel("Sortino ratio")
    ax.set_xlabel("Date")
    fig.legend()

    theme.style_primary_axis(ax)
    theme.visualize_output()


def display_omega(
    data: pd.DataFrame, threshold_start: float = 0, threshold_end: float = 1.5
):
    """Displays the omega ratio
    Parameters
    ----------
    data: pd.DataFrame
        stock dataframe
    threshold_start: float
        annualized target return threshold start of plotted threshold range
    threshold_end: float
        annualized target return threshold end of plotted threshold range
    """
    threshold = np.linspace(threshold_start, threshold_end, 50)
    omega_list = []

    for i in threshold:
        omega_list.append(qa_model.get_omega(data, i))

    # Plotting
    fig, ax = plt.subplots()
    ax.plot(threshold, omega_list)
    ax.set_title(f"Omega Curve - over last {len(data)}'s period")
    ax.set_ylabel("Omega Ratio")
    ax.set_xlabel("Threshold (%)")
    fig.legend()
    ax.set_ylim(threshold_start, threshold_end)

    theme.style_primary_axis(ax)
    theme.visualize_output()
