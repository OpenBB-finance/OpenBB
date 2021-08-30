"""Quantitative Analysis View"""
__docformat__ = "numpy"

import os
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import statsmodels.api as sm
from colorama import Fore, Style
from detecta import detect_cusum
from matplotlib import gridspec
from pandas.plotting import register_matplotlib_converters
from scipy import stats
from statsmodels.graphics.gofplots import qqplot
from tabulate import tabulate

from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.common.quantitative_analysis import qa_model
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.helper_funcs import export_data, plot_autoscale

register_matplotlib_converters()

# TODO : Since these are common/ they should be independent of 'stock' info.
# df_stock should be replaced with a generic df and a column variable


def color_red(val: Any) -> str:
    """Adds red to dataframe value"""
    return Fore.RED + str(val) + Style.RESET_ALL


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

    print(
        tabulate(
            summary, headers=summary.columns, tablefmt="fancy_grid", floatfmt=".3f"
        ),
        "\n",
    )
    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        "summary",
        summary,
    )


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
    start = df.index[0]

    sns.histplot(data, bins=bins, kde=True, ax=ax, stat="proportion")
    sns.rugplot(data, c="r", ax=ax)

    ax.set_title(f"Histogram of {name} {target} from {start.strftime('%Y-%m-%d')}")
    ax.set_xlabel("Share Price")
    ax.grid(True)

    if gtff.USE_ION:
        plt.ion()
    fig.tight_layout()
    plt.show()
    print("")


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
    print("")
    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        "cdf",
        pd.DataFrame(cdf),
    )


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
    print("")


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
    print("")


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
    print("")


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
    print("")

    # From  # https://otexts.com/fpp2/seasonal-strength.html

    print("Time-Series Level is " + str(round(data.mean(), 2)))

    Ft = max(0, 1 - np.var(result.resid)) / np.var(result.trend + result.resid)
    print("Strength of Trend: %.4f" % Ft)
    Fs = max(
        0,
        1 - np.var(result.resid) / np.var(result.seasonal + result.resid),
    )
    print("Strength of Seasonality: %.4f" % Fs, "\n")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        "summary",
        cycle.join(trend),
    )


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
    stats1 = normal.copy()
    stats1.loc[:, stats1.iloc[1, :] > 0.05] = stats1.loc[
        :, stats1.iloc[1, :] > 0.05
    ].apply(lambda x: color_red(x[0]), axis=1)
    if gtff.USE_TABULATE_DF:
        print(
            tabulate(
                stats1,
                showindex=True,
                headers=normal.columns,
                tablefmt="fancy_grid",
                floatfmt=".4f",
            ),
            "\n",
        )
    else:
        print(normal.round(4).to_string(), "\n")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        "normality",
        normal,
    )


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
    print("")


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
    if gtff.USE_TABULATE_DF:
        print(
            tabulate(
                data,
                showindex=True,
                headers=data.columns,
                tablefmt="fancy_grid",
                floatfmt=".4f",
            ),
            "\n",
        )
    else:
        print(data.round(4).to_string(), "\n")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        "unitroot",
        data,
    )
