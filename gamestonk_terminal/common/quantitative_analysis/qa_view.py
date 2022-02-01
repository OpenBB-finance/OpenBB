"""Quantitative Analysis View"""
__docformat__ = "numpy"

import logging
import os
import warnings
from datetime import datetime
from typing import Any

import matplotlib
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import statsmodels.api as sm
from detecta import detect_cusum
from matplotlib import gridspec
from pandas.plotting import register_matplotlib_converters
from scipy import stats
from statsmodels.graphics.gofplots import qqplot

from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.common.quantitative_analysis import qa_model
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.helper_classes import LineAnnotateDrawer
from gamestonk_terminal.helper_funcs import (
    export_data,
    plot_autoscale,
    print_rich_table,
)
from gamestonk_terminal.rich_config import console

logger = logging.getLogger(__name__)

register_matplotlib_converters()

# TODO : Since these are common/ they should be independent of 'stock' info.
# df_stock should be replaced with a generic df and a column variable


@log_start_end(log=logger)
def color_red(val: Any) -> str:
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
):
    """Generate of histogram of data

    Parameters
    ----------
    name : str
        Name of dataset
    df : pd.DataFrame
        Dataframe to look at
    target : str
        Data column to get histogram of
    bins : int
        Number of bins in histogram
    """
    fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    data = df[target]

    sns.histplot(data, bins=bins, kde=True, ax=ax, stat="proportion")
    sns.rugplot(data, c="r", ax=ax)

    if isinstance(df.index[0], datetime):
        start = df.index[0]

        ax.set_title(f"Histogram of {name} {target} from {start.strftime('%Y-%m-%d')}")
    else:
        ax.set_title(f"Histogram of {name} {target}")

    ax.set_xlabel("Value")
    ax.grid(True)

    if gtff.USE_ION:
        plt.ion()
    fig.tight_layout()
    plt.show()
    console.print("")


@log_start_end(log=logger)
def display_cdf(
    name: str,
    df: pd.DataFrame,
    target: str,
    export: str = "",
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
    """
    plt.figure(figsize=plot_autoscale(), dpi=PLOT_DPI)
    data = df[target]
    start = df.index[0]

    cdf = data.value_counts().sort_index().div(len(data)).cumsum()
    cdf.plot(lw=2)
    plt.title(
        f"Cumulative Distribution Function of {name} {target} from {start.strftime('%Y-%m-%d')}"
    )
    plt.ylabel("Probability")
    plt.xlabel(target)
    minVal = data.values.min()
    q25 = np.quantile(data.values, 0.25)
    medianVal = np.quantile(data.values, 0.5)
    q75 = np.quantile(data.values, 0.75)
    labels = [
        (minVal, q25),
        (0.25, 0.25),
        "r",
        (q25, q25),
        (0, 0.25),
        "r",
        (minVal, medianVal),
        (0.5, 0.5),
        "r",
        (medianVal, medianVal),
        (0, 0.5),
        "r",
        (minVal, q75),
        (0.75, 0.75),
        "r",
        (q75, q75),
        (0, 0.75),
        "r",
    ]
    plt.plot(*labels, ls="--")
    plt.text(minVal + (q25 - minVal) / 2, 0.27, "Q1", color="r", fontweight="bold")
    plt.text(
        minVal + (medianVal - minVal) / 2,
        0.52,
        "Median",
        color="r",
        fontweight="bold",
    )
    plt.text(minVal + (q75 - minVal) / 2, 0.77, "Q3", color="r", fontweight="bold")
    plt.xlim(cdf.index[0], cdf.index[-1])
    plt.grid(True)

    if gtff.USE_ION:
        plt.ion()

    plt.show()
    console.print("")
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
    """
    plt.figure(figsize=plot_autoscale(), dpi=PLOT_DPI)
    data = df[target]
    start = df.index[0]
    sns.set(style="whitegrid")
    if yearly:
        box_plot = sns.boxplot(x=data.index.year, y=data)
    else:
        box_plot = sns.boxplot(x=data.index.month, y=data)

    box_plot.set(
        xlabel=["Month", "Year"][yearly],
        ylabel=target,
        title=f"{['Month','Year'][yearly]} BoxPlot of {name} {target} from {start.strftime('%Y-%m-%d')}",
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

    if gtff.USE_ION:
        plt.ion()

    plt.show()
    console.print("")


@log_start_end(log=logger)
def display_acf(name: str, df: pd.DataFrame, target: str, lags: int):
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
    """
    df = df[target]
    start = df.index[0]
    fig = plt.figure(figsize=plot_autoscale(), dpi=PLOT_DPI, constrained_layout=True)
    spec = gridspec.GridSpec(ncols=2, nrows=2, figure=fig)

    # Diff Auto-correlation function for original time series
    ax_acf = fig.add_subplot(spec[0, 0])
    sm.graphics.tsa.plot_acf(np.diff(np.diff(df.values)), lags=lags, ax=ax_acf)
    plt.title(f"{name} Returns Auto-Correlation from {start.strftime('%Y-%m-%d')}")
    # Diff Partial auto-correlation function for original time series
    ax_pacf = fig.add_subplot(spec[0, 1])
    sm.graphics.tsa.plot_pacf(np.diff(np.diff(df.values)), lags=lags, ax=ax_pacf)
    plt.title(
        f"{name} Returns Partial Auto-Correlation from {start.strftime('%Y-%m-%d')}"
    )

    # Diff Diff Auto-correlation function for original time series
    ax_acf = fig.add_subplot(spec[1, 0])
    sm.graphics.tsa.plot_acf(np.diff(np.diff(df.values)), lags=lags, ax=ax_acf)
    plt.title(
        f"Change in {name} Returns Auto-Correlation from {start.strftime('%Y-%m-%d')}"
    )
    # Diff Diff Partial auto-correlation function for original time series
    ax_pacf = fig.add_subplot(spec[1, 1])
    sm.graphics.tsa.plot_pacf(np.diff(np.diff(df.values)), lags=lags, ax=ax_pacf)
    plt.title(
        f"Change in {name}) Returns Partial Auto-Correlation from {start.strftime('%Y-%m-%d')}"
    )

    if gtff.USE_ION:
        plt.ion()

    plt.show()
    console.print("")


@log_start_end(log=logger)
def display_cusum(df: pd.DataFrame, target: str, threshold: float, drift: float):
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
    """
    detect_cusum(df[target].values, threshold, drift, True, True)
    if gtff.USE_ION:
        plt.ion()
    plt.show()
    console.print("")


@log_start_end(log=logger)
def display_seasonal(
    name: str,
    df: pd.DataFrame,
    target: str,
    multiplicative: bool = False,
    export: str = "",
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
    """
    data = df[target]
    fig = plt.figure(figsize=plot_autoscale(), dpi=PLOT_DPI, constrained_layout=True)
    spec = gridspec.GridSpec(ncols=4, nrows=5, figure=fig)
    fig.add_subplot(spec[0, :])
    plt.plot(data.index, data.values)
    plt.title(name + " (Time-Series)")

    result, cycle, trend = qa_model.get_seasonal_decomposition(data, multiplicative)

    # Multiplicative model
    fig.add_subplot(spec[1, :4])
    plt.plot(result.trend, lw=2, c="purple")
    plt.xlim([data.index[0], data.index[-1]])
    plt.title("Cyclic-Trend")

    fig.add_subplot(spec[2, 0:2])
    plt.plot(trend, lw=2, c="tab:blue")
    plt.xlim([data.index[0], data.index[-1]])
    plt.title("Trend component")

    fig.add_subplot(spec[2, 2:])
    plt.plot(cycle, lw=2, c="green")
    plt.xlim([data.index[0], data.index[-1]])
    plt.title("Cycle component")

    fig.add_subplot(spec[3, :])
    plt.plot(result.seasonal, lw=2, c="orange")
    plt.xlim([data.index[0], data.index[-1]])
    plt.title("Seasonal effect")

    fig.add_subplot(spec[4, :])
    plt.plot(result.resid, lw=2, c="red")
    plt.xlim([data.index[0], data.index[-1]])
    plt.title("Residuals")

    if gtff.USE_ION:
        plt.ion()

    plt.show()
    console.print("")

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
    stats1.iloc[:, 1] = stats1.iloc[:, 1].apply(lambda x: color_red(x))

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
def display_qqplot(name: str, df: pd.DataFrame, target: str):
    """Show QQ plot for data against normal quantiles

    Parameters
    ----------
    name : str
        Stock ticker
    df : pd.DataFrame
        Dataframe
    target : str
        Column in data to look at
    """
    # Statsmodels has a UserWarning for marker kwarg-- which we don't use
    warnings.filterwarnings(category=UserWarning, action="ignore")
    data = df[target]
    fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    qqplot(data, stats.distributions.norm, fit=True, line="45", ax=ax)
    ax.set_title(f"Q-Q plot for {name} {target}")
    ax.set_ylabel("Sample quantiles")
    ax.set_xlabel("Theoretical quantiles")
    ax.grid(True)

    if gtff.USE_ION:
        plt.ion()
    fig.tight_layout(pad=1)
    plt.show()
    console.print("")


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
        df = pd.DataFrame(df)

    if sort:
        df = df.sort_values(by=sort, ascending=des)
    df.index = [x.strftime("%Y-%m-%d") for x in df.index]
    print_rich_table(
        df.tail(num),
        headers=[x.title() if x != "" else "Date" for x in df.columns],
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
    export: str = "",
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
    export: str
        Format to export data
    """
    console.print("")
    fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)

    if log_y:
        ax.semilogy(data.index, data.values)
        ax.yaxis.set_major_formatter(matplotlib.ticker.ScalarFormatter())
        ax.yaxis.set_major_locator(
            matplotlib.ticker.LogLocator(base=100, subs=[1.0, 2.0, 5.0, 10.0])
        )
        ax.ticklabel_format(style="plain", axis="y")

    else:
        ax.plot(data.index, data.values)

    ax.grid("on")
    dateFmt = mdates.DateFormatter("%Y-%m-%d")
    ax.xaxis.set_major_formatter(dateFmt)
    ax.tick_params(axis="x", labelrotation=45)
    ax.set_xlabel("Date")
    if title:
        fig.suptitle(title)
    fig.tight_layout(pad=2)

    if gtff.USE_ION:
        plt.ion()
    if gtff.USE_WATERMARK:
        ax.text(
            0.73,
            0.025,
            "Gamestonk Terminal",
            transform=ax.transAxes,
            fontsize=12,
            color="gray",
            alpha=0.5,
        )

    if draw:
        LineAnnotateDrawer(ax).draw_lines_and_annotate()

    plt.show()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        "line",
    )


def display_var(
    data: pd.DataFrame, use_mean: bool, ticker: str, adjusted_var: bool, percentile: int
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
    percentile: int
        var percentile
    """
    var_list, hist_var_list = qa_model.get_var(data, use_mean, adjusted_var, percentile)

    str_hist_label = "Historical VaR:"

    if adjusted_var:
        str_var_label = "Adjusted Var:"
        str_title = "Adjusted "
    else:
        str_var_label = "VaR:"
        str_title = ""

    data_dictionary = {str_var_label: var_list, str_hist_label: hist_var_list}
    data = pd.DataFrame(
        data_dictionary, index=["90.0%", "95.0%", "99.0%", f"{percentile*100}%"]
    )

    print_rich_table(
        data,
        show_index=True,
        headers=list(data.columns),
        title=f"[bold]{ticker} {str_title}Value at Risk[/bold]",
        floatfmt=".4f",
    )
    console.print("")
