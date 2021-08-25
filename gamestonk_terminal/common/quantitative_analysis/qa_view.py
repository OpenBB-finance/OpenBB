"""Quantitative Analysis Views"""
__docformat__ = "numpy"

import os

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


def color_red(val):
    """Adds red to dataframe"""
    return Fore.RED + str(val) + Style.RESET_ALL


def display_summary(df_stock: pd.DataFrame, export: str):
    """Show summary statistics

    Parameters
    ----------
    df_stock : pd.DataFrame
        DataFrame of prices
    prices : bool
        Whether to return statistics of prices instead of returns
    export : str
        Format to export data
    """
    df_stock["Returns"] = df_stock["Adj Close"].pct_change()
    df_stock = df_stock.dropna()

    summary = qa_model.summary(df_stock)

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
    s_ticker: str,
    start: pd.Timestamp,
    df_stock: pd.DataFrame,
    prices: bool,
    bins: int,
):
    """Generate histogram.

    Parameters
    ----------
    s_ticker : str
        Stock ticker
    start : pd.Timestamp
        Start date of data
    df_stock : pd.DataFrame
        Dataframe of prices
    prices : bool
        Flag indicating to show histogram of prices.
    bins : int
        Number of bins in histogram
    """
    fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)

    data = df_stock["Adj Close"]
    if not prices:
        data = data.pct_change().dropna()

    sns.histplot(data, bins=bins, kde=True, ax=ax, stat="proportion")
    sns.rugplot(data, c="r", ax=ax)

    dataset = ["Returns", "Prices"][prices]
    ax.set_title(f"Histogram of {s_ticker} {dataset} from {start.strftime('%Y-%m-%d')}")
    ax.set_xlabel("Share Price")
    ax.grid(True)

    if gtff.USE_ION:
        plt.ion()
    fig.tight_layout()
    plt.show()
    print("")


def display_cdf(
    s_ticker: str,
    start: pd.Timestamp,
    df_stock: pd.DataFrame,
    prices: bool,
    export: str,
):
    """Plot Cumulative Distribution Function

    Parameters
    ----------
    s_ticker : str
        Stock ticker
    start : pd.Timestamp
        Start date of data
    df_stock : pd.DataFrame
        Dataframe of prices
    prices : bool
        Flag to show prices instead of returns
    export : str
        Format to export cdf
    """

    plt.figure(figsize=plot_autoscale(), dpi=PLOT_DPI)

    if prices:
        stock = df_stock["Adj Close"]

    else:
        stock = df_stock["Adj Close"].pct_change().dropna()

    cdf = stock.value_counts().sort_index().div(len(stock)).cumsum()
    cdf.plot(lw=2)
    plt.title(
        f"Cumulative Distribution Function of {s_ticker} {['Returns', 'Price'][prices]} from {start.strftime('%Y-%m-%d')}"
    )
    plt.ylabel("Probability")
    plt.xlabel(["Returns", "Share Price"][prices])
    minVal = stock.values.min()
    q25 = np.quantile(stock.values, 0.25)
    medianVal = np.quantile(stock.values, 0.5)
    q75 = np.quantile(stock.values, 0.75)
    data = [
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
    plt.plot(*data, ls="--")
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
    s_ticker: str,
    start: pd.Timestamp,
    df_stock: pd.DataFrame,
    yearly: bool,
    prices: bool,
):
    """Show box and whisker plots

    Parameters
    ----------
    s_ticker : str
        Stock ticker
    start : pd.Timestamp
        Start date of data
    df_stock : pd.DataFrame
        Dataframe of prices
    yearly : bool
        Flag to indicate yearly accumulation
    prices : bool
        Flag to show raw prices, not returns
    """
    plt.figure(figsize=plot_autoscale(), dpi=PLOT_DPI)

    price_or_returns = ["Returns", "Price"][prices]
    if prices:
        stock = df_stock["Adj Close"]
    else:
        stock = df_stock["Adj Close"].pct_change().dropna()

    sns.set(style="whitegrid")
    if yearly:
        box_plot = sns.boxplot(x=stock.index.year, y=stock)
    else:
        box_plot = sns.boxplot(x=stock.index.month, y=stock)

    box_plot.set(
        xlabel=["Month", "Year"][yearly],
        ylabel=price_or_returns,
        title=f"{['Month','Year'][yearly]} BoxPlot of {s_ticker} {price_or_returns} from {start.strftime('%Y-%m-%d')}",
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


def display_acf(s_ticker: str, start: pd.Timestamp, df_stock: pd.DataFrame, lags: int):
    """Show Auto and Partial Auto Correlation of returns and change in returns

    Parameters
    ----------
    s_ticker : str
        Stock ticker
    start : pd.Timestamp
        Start date of data
    df_stock : pd.DataFrame
        Dataframe of prices
    lags : int
        Max number of lags to look at
    """
    df_stock = df_stock["Adj Close"]

    fig = plt.figure(figsize=plot_autoscale(), dpi=PLOT_DPI, constrained_layout=True)
    spec = gridspec.GridSpec(ncols=2, nrows=2, figure=fig)

    # Diff Auto-correlation function for original time series
    ax_acf = fig.add_subplot(spec[0, 0])
    sm.graphics.tsa.plot_acf(np.diff(np.diff(df_stock.values)), lags=lags, ax=ax_acf)
    plt.title(f"{s_ticker} Returns Auto-Correlation from {start.strftime('%Y-%m-%d')}")
    # Diff Partial auto-correlation function for original time series
    ax_pacf = fig.add_subplot(spec[0, 1])
    sm.graphics.tsa.plot_pacf(np.diff(np.diff(df_stock.values)), lags=lags, ax=ax_pacf)
    plt.title(
        f"{s_ticker} Returns Partial Auto-Correlation from {start.strftime('%Y-%m-%d')}"
    )

    # Diff Diff Auto-correlation function for original time series
    ax_acf = fig.add_subplot(spec[1, 0])
    sm.graphics.tsa.plot_acf(np.diff(np.diff(df_stock.values)), lags=lags, ax=ax_acf)
    plt.title(
        f"Change in {s_ticker} Returns Auto-Correlation from {start.strftime('%Y-%m-%d')}"
    )
    # Diff Diff Partial auto-correlation function for original time series
    ax_pacf = fig.add_subplot(spec[1, 1])
    sm.graphics.tsa.plot_pacf(np.diff(np.diff(df_stock.values)), lags=lags, ax=ax_pacf)
    plt.title(
        f"Change in {s_ticker}) Returns Partial Auto-Correlation from {start.strftime('%Y-%m-%d')}"
    )

    if gtff.USE_ION:
        plt.ion()

    plt.show()
    print("")


def display_cusum(df_stock: pd.DataFrame, threshold: float, drift: float):
    """Cumulative sum algorithm (CUSUM) to detect abrupt changes in data

    Parameters
    ----------
    df_stock : pd.DataFrame
        Datafrme of prices
    threshold : float
        Threshold value
    drift : float
        Drift parameter
    """
    detect_cusum(df_stock["Adj Close"].values, threshold, drift, True, True)

    if gtff.USE_ION:
        plt.ion()

    plt.show()
    print("")


def display_seasonal(
    s_ticker: str, df_stock: pd.DataFrame, multiplicative: bool, export: str
):
    """[summary]

    Parameters
    ----------
    s_ticker : str
        Stock ticker
    df_stock : pd.DataFrame
        DataFrame of stock prices
    multiplicative : bool
        Boolean to indicate multiplication instead of addition
    export : str
        Format to export trend and cycle df
    """
    stock = df_stock["Adj Close"]

    fig = plt.figure(figsize=plot_autoscale(), dpi=PLOT_DPI, constrained_layout=True)
    spec = gridspec.GridSpec(ncols=4, nrows=5, figure=fig)

    fig.add_subplot(spec[0, :])
    plt.plot(stock.index, stock.values)

    plt.title(s_ticker + " (Time-Series)")

    result, cycle, trend = qa_model.seasonal_decomposition(stock, multiplicative)

    # Multiplicative model
    fig.add_subplot(spec[1, :4])
    plt.plot(result.trend, lw=2, c="purple")
    plt.xlim([stock.index[0], stock.index[-1]])
    plt.title("Cyclic-Trend")

    fig.add_subplot(spec[2, 0:2])
    plt.plot(trend, lw=2, c="tab:blue")
    plt.xlim([stock.index[0], stock.index[-1]])
    plt.title("Trend component")

    fig.add_subplot(spec[2, 2:])
    plt.plot(cycle, lw=2, c="green")
    plt.xlim([stock.index[0], stock.index[-1]])
    plt.title("Cycle component")

    fig.add_subplot(spec[3, :])
    plt.plot(result.seasonal, lw=2, c="orange")
    plt.xlim([stock.index[0], stock.index[-1]])
    plt.title("Seasonal effect")

    fig.add_subplot(spec[4, :])
    plt.plot(result.resid, lw=2, c="red")
    plt.xlim([stock.index[0], stock.index[-1]])
    plt.title("Residuals")

    if gtff.USE_ION:
        plt.ion()

    plt.show()
    print("")

    # From  # https://otexts.com/fpp2/seasonal-strength.html

    print("Time-Series Level is " + str(round(stock.mean(), 2)))

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


def display_normality(df_stock: pd.DataFrame, prices: bool, export: str):
    """View normality statistics

    Parameters
    ----------
    df_stock : pd.DataFrame
        [description]
    prices : bool
        [description]
    export : str
        [description]
    """
    normal = qa_model.normality(df_stock, prices)
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


def display_qqplot(s_ticker: str, df_stock: pd.DataFrame, prices: bool):
    """Show QQ plot for returns against normal quantiles

    Parameters
    ----------
    s_ticker : str
        Stock ticker
    df_stock : pd.DataFrame
        Dataframe of prices
    prices : bool
        Flag to show prices instead of returns
    """
    if prices:
        data = df_stock["Adj Close"]
    else:
        data = df_stock["Adj Close"].pct_change().dropna()
    showing = ["Returns", "Price"][prices]
    fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    qqplot(data, stats.distributions.norm, fit=True, line="45", ax=ax)
    ax.set_title(f"Q-Q plot for {s_ticker} {showing}")
    ax.set_ylabel("Sample quantiles")
    ax.set_xlabel("Theoretical quantiles")
    ax.grid(True)

    if gtff.USE_ION:
        plt.ion()
    fig.tight_layout(pad=1)
    plt.show()
    print("")


def display_unitroot(
    df_stock: pd.DataFrame, prices: bool, fuller_reg: str, kpss_reg: str, export: str
):
    """Show unit root test calculations

    Parameters
    ----------
    df_stock : pd.DataFrame
        DataFrame of prices
    prices : bool
        Whether to perform test on prices instead of returns
    fuller_reg : str
        Type of regression of ADF test
    kpss_reg : str
        Type of regression for KPSS test
    export : str
        Format for exporting data
    """
    data = qa_model.unitroot(df_stock, prices, fuller_reg, kpss_reg)
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
