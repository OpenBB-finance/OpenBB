""" Exploratory Data Analysis API """
__docformat__ = "numpy"

import argparse
from typing import List
from datetime import datetime
from detecta import detect_cusum
from matplotlib import pyplot as plt
import pandas as pd
from pandas.plotting import register_matplotlib_converters
import numpy as np
import seaborn as sns
import statsmodels.api as sm
import matplotlib.gridspec as gridspec
from statsmodels.tsa.seasonal import seasonal_decompose
from gamestonk_terminal.helper_funcs import (
    parse_known_args_and_warn,
    plot_autoscale,
    check_positive,
)
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal import feature_flags as gtff


register_matplotlib_converters()


def summary(other_args: List[str], stock: pd.DataFrame):
    """Print summary statistics

    Parameters
    ----------
    other_args : str
        Command line arguments to be processed with argparse
    ticker : str
        Ticker of the stock
    stock : pd.DataFrame
        Stock data
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        prog="summary",
        description="""
            Summary statistics
        """,
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        df_stats = stock.describe(percentiles=[0.1, 0.25, 0.5, 0.75, 0.9])
        df_stats.loc["var"] = df_stats.loc["std"] ** 2
        print(df_stats.round(2).to_string())

        print("")

    except Exception as e:
        print(e, "\n")
        return


def hist(other_args: List[str], ticker: str, stock: pd.DataFrame, start: datetime):
    """Plot histogram and density

    Parameters
    ----------
    other_args : str
        Command line arguments to be processed with argparse
    ticker : str
        Ticker of the stock
    stock : pd.DataFrame
        Stock data
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        prog="hist",
        description="""
            Histogram with depicted density and rug
        """,
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        plt.figure(figsize=plot_autoscale(), dpi=PLOT_DPI)

        stock = stock["Adj Close"]

        sns.distplot(
            stock,
            bins=35,
            color="blue",
            hist=True,
            hist_kws={"edgecolor": "black"},
            kde=True,
            kde_kws={"color": "black", "lw": 3, "label": "KDE"},
            rug=True,
            rug_kws={"edgecolor": "orange"},
        )
        plt.title(
            f"Histogram with Density of {ticker} from {start.strftime('%Y-%m-%d')}"
        )
        plt.ylabel("Density")
        plt.xlabel("Share Price")
        plt.grid(True)

        if gtff.USE_ION:
            plt.ion()

        plt.show()
        print("")

    except Exception as e:
        print(e, "\n")
        return


def cumulative_distribution_function(
    other_args: List[str], ticker: str, stock: pd.DataFrame, start: datetime
):
    """Plot cumulative distribution function

    Parameters
    ----------
    other_args : str
        Command line arguments to be processed with argparse
    ticker : str
        Ticker of the stock
    stock : pd.DataFrame
        Stock data
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        prog="cdf",
        description="""
            Cumulative distribution function
        """,
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        plt.figure(figsize=plot_autoscale(), dpi=PLOT_DPI)

        stock = stock["Adj Close"]

        cdf = stock.value_counts().sort_index().div(len(stock)).cumsum()
        cdf.plot(lw=2)
        plt.title(
            f"Cumulative Distribution Function of {ticker} from {start.strftime('%Y-%m-%d')}"
        )
        plt.ylabel("Probability")
        plt.xlabel("Share Price")
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

    except Exception as e:
        print(e, "\n")
        return


def bwy(other_args: List[str], ticker: str, stock: pd.DataFrame, start: datetime):
    """Box and Whisker plot yearly

    Parameters
    ----------
    other_args : str
        Command line arguments to be processed with argparse
    ticker : str
        Ticker of the stock
    stock : pd.DataFrame
        Stock data
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        prog="bwy",
        description="""
            Box and Whisker plot yearly
        """,
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        plt.figure(figsize=plot_autoscale(), dpi=PLOT_DPI)

        stock = stock["Adj Close"]

        sns.set(style="whitegrid")
        box_plot = sns.boxplot(x=stock.index.year, y=stock)
        box_plot.set(
            xlabel="Year",
            ylabel="Share Price",
            title=f"Box-plot per Year of {ticker} from {start.strftime('%Y-%m-%d')}",
        )

        if gtff.USE_ION:
            plt.ion()

        plt.show()
        print("")

    except Exception as e:
        print(e, "\n")
        return


def bwm(other_args: List[str], ticker: str, stock: pd.DataFrame, start: datetime):
    """Box and Whisker plot monthly

    Parameters
    ----------
    other_args : str
        Command line arguments to be processed with argparse
    ticker : str
        Ticker of the stock
    stock : pd.DataFrame
        Stock data
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        prog="bwm",
        description="""
            Box and Whisker plot monthly
        """,
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        plt.figure(figsize=plot_autoscale(), dpi=PLOT_DPI)

        stock = stock["Adj Close"]

        sns.set(style="whitegrid")
        box_plot = sns.boxplot(x=stock.index.month, y=stock)
        box_plot.set(
            xlabel="Month",
            ylabel="Share Price",
            title=f"Box-plot per Month of {ticker} from {start.strftime('%Y-%m-%d')}",
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
        for val in box_plot.get_xticklabels():
            l_ticks.append(l_months[int(val.get_text()) - 1])
        box_plot.set_xticklabels(l_ticks)

        if gtff.USE_ION:
            plt.ion()

        plt.show()
        print("")

    except Exception as e:
        print(e, "\n")
        return


def rolling(other_args: List[str], ticker: str, stock: pd.DataFrame):
    """Rolling mean and std deviation

    Parameters
    ----------
    other_args : str
        Command line arguments to be processed with argparse
    ticker : str
        Ticker of the stock
    stock : pd.DataFrame
        Stock data
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        prog="rolling",
        description="""
            Rolling mean and std deviation
        """,
    )
    parser.add_argument(
        "-w",
        "--window",
        dest="rolling_window",
        type=check_positive,
        default=10,
        help="rolling window",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        stock = stock["Adj Close"]

        rolling_mean = stock.rolling(
            ns_parser.rolling_window, center=True, min_periods=1
        ).mean()
        rolling_std = stock.rolling(
            ns_parser.rolling_window, center=True, min_periods=1
        ).std()

        _, axMean = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)

        axMean.plot(stock.index, stock.values, label=ticker, linewidth=2, color="black")
        axMean.plot(rolling_mean, linestyle="--", linewidth=3, color="blue")
        axMean.set_xlabel("Time")
        axMean.set_ylabel("Share Price", color="blue")
        axMean.legend(["Real values", "Rolling Mean"], loc=2)
        axMean.tick_params(axis="y", labelcolor="blue")
        axStd = axMean.twinx()
        axStd.plot(
            rolling_std, label="Rolling std", linestyle="--", color="green", linewidth=3
        )
        axStd.set_ylabel("Std Deviation")
        axStd.legend(["Rolling std"], loc=1)
        axStd.set_ylabel("Share Price standard deviation", color="green")
        axStd.tick_params(axis="y", labelcolor="green")
        axMean.set_title(
            "Rolling mean and std with window "
            + str(ns_parser.rolling_window)
            + " applied to "
            + ticker
        )
        plt.xlim([stock.index[0], stock.index[-1]])
        plt.grid(b=True, which="major", color="#666666", linestyle="-")
        plt.minorticks_on()
        plt.grid(b=True, which="minor", color="#999999", linestyle="-", alpha=0.2)

        if gtff.USE_ION:
            plt.ion()

        plt.show()
        print("")

    except Exception as e:
        print(e, "\n")
        return


def decompose(other_args: List[str], ticker: str, stock: pd.DataFrame):
    """Decompose time series as:
        - Additive Time Series = Level + CyclicTrend + Residual + Seasonality
        - Multiplicative Time Series = Level * CyclicTrend * Residual * Seasonality

    Parameters
    ----------
    other_args : str
        Command line arguments to be processed with argparse
    ticker : str
        Ticker of the stock
    stock : pd.DataFrame
        Stock data
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        prog="decompose",
        description="""
            Decompose time series as:
              - Additive Time Series = Level + CyclicTrend + Residual + Seasonality
              - Multiplicative Time Series = Level * CyclicTrend * Residual * Seasonality
        """,
    )
    parser.add_argument(
        "-m",
        "--multiplicative",
        action="store_true",
        default=False,
        dest="multiplicative",
        help="decompose using multiplicative model instead of additive",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        stock = stock["Adj Close"]

        seasonal_periods = 5
        # Hodrick-Prescott filter
        # See Ravn and Uhlig: http://home.uchicago.edu/~huhlig/papers/uhlig.ravn.res.2002.pdf
        lamb = 107360000000

        fig = plt.figure(
            figsize=plot_autoscale(), dpi=PLOT_DPI, constrained_layout=True
        )
        spec = gridspec.GridSpec(ncols=4, nrows=5, figure=fig)

        fig.add_subplot(spec[0, :])
        plt.plot(stock)

        plt.title(ticker + " (Time-Series)")

        if ns_parser.multiplicative:
            resultMul = seasonal_decompose(
                stock, model="multiplicative", period=seasonal_periods
            )
            cycleMul, trendMul = sm.tsa.filters.hpfilter(
                resultMul.trend[resultMul.trend.notna().values], lamb=lamb
            )

            # Multiplicative model
            fig.add_subplot(spec[1, :4])
            plt.plot(resultMul.trend, lw=2, c="purple")
            plt.xlim([stock.index[0], stock.index[-1]])
            plt.title("Multiplicative Cyclic-Trend")

            fig.add_subplot(spec[2, 0:2])
            plt.plot(trendMul, lw=2, c="tab:blue")
            plt.xlim([stock.index[0], stock.index[-1]])
            plt.title("Multiplicative Trend component")

            fig.add_subplot(spec[2, 2:])
            plt.plot(cycleMul, lw=2, c="green")
            plt.xlim([stock.index[0], stock.index[-1]])
            plt.title("Multiplicative Cycle component")

            fig.add_subplot(spec[3, :])
            plt.plot(resultMul.seasonal, lw=2, c="orange")
            plt.xlim([stock.index[0], stock.index[-1]])
            plt.title("Multiplicative Seasonal effect")

            fig.add_subplot(spec[4, :])
            plt.plot(resultMul.resid, lw=2, c="red")
            plt.xlim([stock.index[0], stock.index[-1]])
            plt.title("Multiplicative Residuals")

        else:
            resultAdd = seasonal_decompose(
                stock, model="additive", period=seasonal_periods
            )
            cycleAdd, trendAdd = sm.tsa.filters.hpfilter(
                resultAdd.trend[resultAdd.trend.notna().values], lamb=lamb
            )

            # Additive model
            fig.add_subplot(spec[1, :4])
            plt.plot(resultAdd.trend, lw=2, c="purple")
            plt.xlim([stock.index[0], stock.index[-1]])
            plt.title("Additive Cyclic-Trend")

            fig.add_subplot(spec[2, 0:2])
            plt.plot(trendAdd, lw=2, c="tab:blue")
            plt.xlim([stock.index[0], stock.index[-1]])
            plt.title("Additive Trend component")

            fig.add_subplot(spec[2, 2:])
            plt.plot(cycleAdd, lw=2, c="green")
            plt.xlim([stock.index[0], stock.index[-1]])
            plt.title("Additive Cycle component")

            fig.add_subplot(spec[3, :])
            plt.plot(resultAdd.seasonal, lw=2, c="orange")
            plt.xlim([stock.index[0], stock.index[-1]])
            plt.title("Additive Seasonal effect")

            fig.add_subplot(spec[4, :])
            plt.plot(resultAdd.resid, lw=2, c="red")
            plt.xlim([stock.index[0], stock.index[-1]])
            plt.title("Additive Residuals")

        if gtff.USE_ION:
            plt.ion()

        plt.show()
        print("")

        # From  # https://otexts.com/fpp2/seasonal-strength.html

        print("Time-Series Level is " + str(round(stock.mean(), 2)))

        if ns_parser.multiplicative:
            FtMul = max(0, 1 - np.var(resultMul.resid)) / np.var(
                resultMul.trend + resultMul.resid
            )
            print("Strength of Trend: %.4f" % FtMul)
            FsMul = max(
                0,
                1
                - np.var(resultMul.resid)
                / np.var(resultMul.seasonal + resultMul.resid),
            )
            print("Strength of Seasonality: %.4f" % FsMul)

        else:
            FtAdd = max(
                0,
                1 - np.var(resultAdd.resid) / np.var(resultAdd.trend + resultAdd.resid),
            )
            print("Strength of Trend: %.4f" % FtAdd)
            FsAdd = max(
                0,
                1
                - np.var(resultAdd.resid)
                / np.var(resultAdd.seasonal + resultAdd.resid),
            )
            print("Strength of Seasonality: %.4f" % FsAdd)
        print("")

    except Exception as e:
        print(e, "\n")
        return


def cusum(other_args: List[str], stock: pd.DataFrame):
    """Cumulative sum algorithm (CUSUM) to detect abrupt changes in data

    Parameters
    ----------
    other_args : str
        Command line arguments to be processed with argparse
    ticker : str
        Ticker of the stock
    stock : pd.DataFrame
        Stock data
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        prog="cusum",
        description="""
            Cumulative sum algorithm (CUSUM) to detect abrupt changes in data
        """,
    )
    parser.add_argument(
        "-t",
        "--threshold",
        dest="threshold",
        type=float,
        default=(max(stock["Adj Close"].values) - min(stock["Adj Close"].values)) / 40,
        help="threshold",
    )
    parser.add_argument(
        "-d",
        "--drift",
        dest="drift",
        type=float,
        default=(max(stock["Adj Close"].values) - min(stock["Adj Close"].values)) / 80,
        help="drift",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        stock = stock["Adj Close"]

        detect_cusum(stock.values, ns_parser.threshold, ns_parser.drift, True, True)

        if gtff.USE_ION:
            plt.ion()

        plt.show()
        print("")

    except Exception as e:
        print(e, "\n")
        return


def acf(other_args: List[str], ticker: str, stock: pd.DataFrame, start: datetime):
    """Auto-Correlation and Partial Auto-Correlation Functions for diff and diff diff stock data

    Parameters
    ----------
    other_args : str
        Command line arguments to be processed with argparse
    ticker : str
        Ticker of the stock
    stock : pd.DataFrame
        Stock data
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        prog="acf",
        description="""
            Auto-Correlation and Partial Auto-Correlation Functions for diff and diff diff stock data
        """,
    )
    parser.add_argument(
        "-l",
        "--lags",
        dest="lags",
        type=check_positive,
        default=15,
        help="maximum lags to display in plots",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        print(stock.head())
        stock = stock["Adj Close"]

        fig = plt.figure(
            figsize=plot_autoscale(), dpi=PLOT_DPI, constrained_layout=True
        )
        spec = gridspec.GridSpec(ncols=2, nrows=2, figure=fig)

        # Diff Auto-correlation function for original time series
        ax_acf = fig.add_subplot(spec[0, 0])
        sm.graphics.tsa.plot_acf(
            np.diff(np.diff(stock.values)), lags=ns_parser.lags, ax=ax_acf
        )
        plt.title(f"Diff({ticker}) Auto-Correlation from {start.strftime('%Y-%m-%d')}")
        # Diff Partial auto-correlation function for original time series
        ax_pacf = fig.add_subplot(spec[0, 1])
        sm.graphics.tsa.plot_pacf(
            np.diff(np.diff(stock.values)), lags=ns_parser.lags, ax=ax_pacf
        )
        plt.title(
            f"Diff({ticker}) Partial Auto-Correlation from {start.strftime('%Y-%m-%d')}"
        )

        # Diff Diff Auto-correlation function for original time series
        ax_acf = fig.add_subplot(spec[1, 0])
        sm.graphics.tsa.plot_acf(
            np.diff(np.diff(stock.values)), lags=ns_parser.lags, ax=ax_acf
        )
        plt.title(
            f"Diff(Diff({ticker})) Auto-Correlation from {start.strftime('%Y-%m-%d')}"
        )
        # Diff Diff Partial auto-correlation function for original time series
        ax_pacf = fig.add_subplot(spec[1, 1])
        sm.graphics.tsa.plot_pacf(
            np.diff(np.diff(stock.values)), lags=ns_parser.lags, ax=ax_pacf
        )
        plt.title(
            f"Diff(Diff({ticker})) Partial Auto-Correlation from {start.strftime('%Y-%m-%d')}"
        )

        if gtff.USE_ION:
            plt.ion()

        plt.show()
        print("")

    except Exception as e:
        print(e, "\n")
        return
