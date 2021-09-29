"""SentimentInvestor View"""
__docformat__ = "numpy"

from typing import List

import matplotlib.dates as mdates
import pandas as pd
import seaborn as sns
import tabulate
from colorama import Style
from matplotlib import pyplot as plt
from sentipy.sentipy import Sentipy

from gamestonk_terminal import config_terminal as cfg
from gamestonk_terminal.common.behavioural_analysis import sentimentinvestor_model
from gamestonk_terminal.common.behavioural_analysis.sentimentinvestor_model import (
    _Boundary,
    _Metric,
)
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.helper_funcs import plot_autoscale

sentipy: Sentipy = Sentipy(
    token=cfg.API_SENTIMENTINVESTOR_TOKEN, key=cfg.API_SENTIMENTINVESTOR_KEY
)
"""Initialise SentiPy with the user's API token and key"""

pd.plotting.register_matplotlib_converters()

# TODO: Make code more consisnet with rest of repository


def display_top(metric: str, limit: int):
    """Displays top stocks from sentimentinvestor based on metric [Source: sentimentinvestor]

    Parameters
    ----------
    metric : str
        Metric to get top for
    limit : int
        Number of tickers to get
    """
    table = sentimentinvestor_model.get_top(metric, limit)
    print(tabulate.tabulate(table, headers=["Rank", "Ticker", metric], floatfmt=".3f"))
    print("")


def _tabulate_metrics(ticker: str, metrics_list: List[_Metric]):
    """Tabulates sentiment investor data"""
    table_data = []
    table_headers = [
        f"{Style.BRIGHT}{ticker}{Style.RESET_ALL} Metrics",
        "vs Past 7 Days",
        "Value",
        "Description",
    ]

    for metric in metrics_list:
        table_data.append(metric.visualise())

    return tabulate.tabulate(table_data, table_headers, tablefmt="grid")


def _customise_plot() -> None:
    """Customizes sentimentinvestor plot"""
    sns.set(
        font="Arial",
        style="darkgrid",
        rc={
            "axes.axisbelow": False,
            "axes.edgecolor": "lightgrey",
            "axes.facecolor": "None",
            "axes.grid": False,
            "axes.labelcolor": "dimgrey",
            "axes.spines.right": False,
            "axes.spines.top": False,
            "figure.facecolor": "white",
            "lines.solid_capstyle": "round",
            "patch.edgecolor": "w",
            "patch.force_edgecolor": True,
            "text.color": "dimgrey",
            "xtick.bottom": False,
            "xtick.color": "dimgrey",
            "xtick.direction": "out",
            "xtick.top": False,
            "ytick.color": "dimgrey",
            "ytick.direction": "out",
            "ytick.left": False,
            "ytick.right": False,
        },
    )
    sns.despine(left=True, bottom=True)
    sns.color_palette("pastel")
    plt.legend(frameon=False)


def display_metrics(ticker: str) -> None:
    """Display sentiment investor metrics for stock ticker"""
    if not sentipy.supported(ticker):
        print("This stock is not supported by the SentimentInvestor API.")
        return

    metric_values = sentimentinvestor_model.get_metrics(ticker)

    if not metric_values:
        print("No data available or an error occurred.")
        return

    print(_tabulate_metrics(ticker, metric_values))
    print()


def display_social(ticker: str) -> None:
    """Display sentiment investor social metrics for ticker"""
    if not sentipy.supported(ticker):
        print("This stock is not supported by the SentimentInvestor API.")
        return

    metric_values = sentimentinvestor_model.get_socials(ticker)

    if not metric_values:
        print("No data available or an error occurred.")
        return

    print(_tabulate_metrics(ticker, metric_values))
    print("")


def display_historical(
    ticker: str, sort_param: str, sort_dir: str, metric: str
) -> None:
    """Show historical sentiment from sentimentinvestor [Source: sentimentinvestor]

    Parameters
    ----------
    ticker : str
        Stock ticker
    sort_param : str
        Parameter to sort table by
    sort_dir : str
        Direction for sorting
    metric : str
        Metric to get data for. Either 'sentiment', 'AHI', 'RHI', 'SGP'
    """
    if not sentipy.supported(ticker):
        print("This stock is not supported by the SentimentInvestor API.")
        return

    df = sentimentinvestor_model.get_historical(ticker, metric)

    if df.empty:
        print("The dataset is empty, something must have gone wrong")
        return

    _customise_plot()

    # use seaborn to lineplot
    ax = sns.lineplot(
        data=df,
        x="date",
        y=metric,
        legend=False,
        label=[metric],
    )

    # always show zero on the y-axis
    plt.ylim(bottom=0)

    # set the x-axis date formatting
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%x"))

    # scale the plot appropriately
    plt.gcf().set_size_inches(plot_autoscale())
    plt.gcf().set_dpi(PLOT_DPI)
    plt.gcf().autofmt_xdate()

    # fill below the line
    plt.fill_between(df.date, df[metric], alpha=0.3)

    # add title e.g. AAPL sentiment since 22/07/21
    plt.title(f"{ticker} {metric} since {min(df.date).strftime('%x')}")

    plt.show()

    ###

    boundary = _Boundary(0, max(df[metric].max(), 2 * df[metric].mean()))

    # average for each day
    aggregated = df.resample("D", on="date").mean()

    # reverse the ordering if requested
    aggregated.sort_values(
        metric if sort_param == "value" else sort_param,
        axis=0,
        ascending=sort_dir == "asc",
        inplace=True,
    )

    # format the date according to user's locale
    aggregated.index = aggregated.index.strftime("%x")

    # apply coloring to every value
    aggregated[metric] = [
        boundary.categorise(value)[0] + str(value) + Style.RESET_ALL
        for value in aggregated[metric]
    ]

    print(
        tabulate.tabulate(
            aggregated,
            headers=["Day", f"average {metric}"],
            tablefmt="psql",
            floatfmt=".3f",
        ),
        "\n",
    )
