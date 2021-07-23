import argparse
import dataclasses
import datetime
import multiprocessing
import os
import statistics
import time
from typing import Union, Optional

import matplotlib.dates as mdates
import pandas as pd
import seaborn as sns
from colorama import Fore, Style
from matplotlib import pyplot as plt
from sentipy.sentipy import Sentipy
from tabulate import tabulate

from gamestonk_terminal import config_terminal as cfg
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.helper_funcs import (
    parse_known_args_and_warn,
    plot_autoscale,
)

sentipy: Sentipy = Sentipy(
    token=cfg.API_SENTIMENTINVESTOR_TOKEN, key=cfg.API_SENTIMENTINVESTOR_KEY)
"""Initialise SentiPy with the user's API token and key"""

pd.plotting.register_matplotlib_converters()


def _bright_text(string: str) -> str:
    """
    Simple wrapper method to make a given string bright (bold on some platforms)

    Parameters
    ----------
    string: the string to brighten

    Returns
    -------
    the brightened string

    """
    return Style.BRIGHT + string + Style.RESET_ALL


@dataclasses.dataclass
class _Boundary:
    """Represents a strong or weak bounding inequality for categorising a value"""

    min: Union[float, int]
    "Minimum value that this metric could take"
    max: Union[float, int]
    "Maximum value that this metric could take"
    strong: bool = False
    "Whether this a strongly bounded inequality"

    def categorise(self, num: Union[float, int]) -> str:
        """
        Categorise a given number using this bounding inequality

        Parameters
        ----------
        num: the number to bucket

        Returns
        -------
        A brightly colored string with low / medium / high as appropriate

        """

        boundaries = [self.min + (self.max - self.min) /
                      5 * i for i in range(1, 5)]

        return _bright_text(
            f"{Fore.WHITE}N/A" if num is None
            else f"{Fore.WHITE}Extreme (anomaly?)" if (num <= self.min or num >= self.max) and self.strong
            else f"{Fore.RED}Much Lower" if num < boundaries[0]
            else f"{Fore.LIGHTRED_EX}Lower" if num < boundaries[1]
            else f"{Fore.YELLOW}Same" if num < boundaries[2]
            else f"{Fore.LIGHTGREEN_EX}Higher" if num < boundaries[3]
            else f"{Fore.GREEN}Much Higher"
        )


def _get_past_week_average(ticker: str, metric: str) -> float:
    historical_data = [dp for dp in sentipy.historical(ticker, metric, int(time.time() - 60 * 60 * 24 * 7),
                                                       int(time.time())).values() if dp is not None]
    return statistics.mean(historical_data) if historical_data else None


@dataclasses.dataclass
class _MetricInfo:
    name: str
    """Metric attribute name"""
    title: str
    """Human-friendly attribute name"""
    description: str
    """Metric attribute description"""
    format: str
    """Format string for presenting the value"""


class _Metric(_MetricInfo):
    boundary: _Boundary
    """A contextual range to for this metric"""
    ticker: str
    """Ticker symbol for which this metric relates"""
    value: Union[float, int]
    """Value"""

    def __init__(self, metric_info: _MetricInfo, ticker: str, value: Union[float, int],
                 boundary: Optional[_Boundary] = None):
        super(_Metric, self).__init__(**dataclasses.asdict(metric_info))

        self.boundary = _Boundary(
            0, 2 * _get_past_week_average(ticker, self.name)) if boundary is None else boundary
        self.ticker = ticker
        self.value = value

    def visualise(self) -> tuple:
        return self.title, \
            self.boundary.categorise(self.value), \
            "N/A" if self.value is None else f"{self.value:{self.format}}", \
            self.description


core_metrics = [
    _MetricInfo('sentiment', "Sentiment Score",
                "the percentage of people that are talking positively about a stock", ".0%"),
    _MetricInfo('AHI', "Average Hype Index",
                "how much people are talking about a stock on social media", ".3f"),
    _MetricInfo('RHI', "Relative Hype Index",
                "whether people are talking about a stock more or less than usual", ".3f"),
    _MetricInfo('SGP', "Standard General Perception",
                "whether people are more or less positive about a stock than usual", ".3f")
]

social_metrics = [
    _MetricInfo('reddit_comment_mentions', "Reddit Comment Mentions",
                "the number of mentions this stock has received in Reddit comments", "n"),
    _MetricInfo('reddit_comment_sentiment', "Reddit Comment Sentiment",
                "percentage of Reddit comments mentioning this stock in a positive light", ".0%"),
    _MetricInfo('reddit_post_mentions', "Reddit Post Mentions",
                "the number of mentions this stock has received in Reddit posts", "n"),
    _MetricInfo('reddit_post_sentiment', "Reddit Post Sentiment",
                "percentage of Reddit posts mentioning this stock in a positive light", ".0%"),
    _MetricInfo('tweet_mentions', "Twitter Mentions",
                "the number of mentions this stock has received on Twitter", "n"),
    _MetricInfo('tweet_sentiment', "Twitter Sentiment",
                "percentage of tweets mentioning this stock in a positive light", ".0%"),
    _MetricInfo('stocktwits_post_mentions', "Stocktwits Mentions",
                "the number of mentions this stock has received in Stocktwits posts", "n"),
    _MetricInfo('stocktwits_post_sentiment', "Stocktwits Sentiment",
                "percentage of Stocktwits posts mentioning this stock in a positive light", ".0%"),
    _MetricInfo('yahoo_finance_comment_mentions', "Yahoo! Finance Comment Mentions",
                "the number of mentions this stock has received in Yahoo! Finance comments", "n"),
    _MetricInfo('yahoo_finance_comment_sentiment', "Yahoo! Finance Comment Sentiment",
                "percentage of Yahoo! Finance comments mentioning this stock in a positive light", ".0%")
]


def _tabulate_metrics(ticker: str, metrics_list: list[_Metric]) -> tabulate:
    table_data = []
    table_headers = [
        f'{_bright_text(ticker)} Metrics', 'vs Past 7 Days', 'Value', 'Description']

    for metric in metrics_list:
        table_data.append(metric.visualise())

    return tabulate(table_data, table_headers, tablefmt="psql")


def _show_metric_descriptions(other_args: list[str]) -> bool:
    if not {'-d', '--desc', '--description', '--descriptions'}.isdisjoint(other_args):
        return True
    elif other_args:
        print(f"Unknown arguments {other_args!r}")
    return False


def _customise_plot() -> None:
    sns.set(font='Open Sans',
            style='darkgrid',
            rc={
                'axes.axisbelow': False,
                'axes.edgecolor': 'lightgrey',
                'axes.facecolor': 'None',
                'axes.grid': False,
                'axes.labelcolor': 'dimgrey',
                'axes.spines.right': False,
                'axes.spines.top': False,
                'figure.facecolor': 'white',
                'lines.solid_capstyle': 'round',
                'patch.edgecolor': 'w',
                'patch.force_edgecolor': True,
                'text.color': 'dimgrey',
                'xtick.bottom': False,
                'xtick.color': 'dimgrey',
                'xtick.direction': 'out',
                'xtick.top': False,
                'ytick.color': 'dimgrey',
                'ytick.direction': 'out',
                'ytick.left': False,
                'ytick.right': False})
    sns.despine(left=True, bottom=True)
    sns.color_palette('pastel')
    plt.legend(frameon=False)


def metrics(ticker: str, other_args: list[str]) -> None:
    parser = argparse.ArgumentParser(add_help=False, prog="metrics",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                     description="Print realtime sentiment and hype index for this stock, aggregated from social media.")

    parser.add_argument("-t", "--ticker", action="store", dest="ticker", type=str, default=ticker,
                        help="ticker for which to fetch the core metrics")

    ns_parser = parse_known_args_and_warn(parser, other_args)
    if not ns_parser:
        return

    data = sentipy.parsed(ns_parser.ticker)

    with multiprocessing.Pool(os.cpu_count()) as pool:
        metric_values = pool.starmap(_Metric, [(metric_info, ns_parser.ticker, data.__getattribute__(metric_info.name))
                                               for metric_info in core_metrics])

    print(_tabulate_metrics(ns_parser.ticker, metric_values))


def socials(ticker: str, other_args: list[str]) -> None:
    parser = argparse.ArgumentParser(add_help=False, prog="social",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                     description="Print the number of mentions and average sentiment of remarks mentioning this stock for several social media sources")
    parser.add_argument("-t", "--ticker", action="store", dest="ticker", type=str, default=ticker,
                        help="ticker for which to fetch the raw social media data")

    ns_parser = parse_known_args_and_warn(parser, other_args)
    if not ns_parser:
        return

    data = sentipy.raw(ns_parser.ticker)

    with multiprocessing.Pool(os.cpu_count()) as pool:
        metric_values = pool.starmap(_Metric, [(metric_info, ns_parser.ticker, data.__getattribute__(metric_info.name))
                                               for metric_info in social_metrics])

    print(_tabulate_metrics(ns_parser.ticker, metric_values))


def historical(ticker: str, other_args: list[str]) -> None:
    parser = argparse.ArgumentParser(add_help=False, prog="historical",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                     description="Plot the past week of data for a specific metric")
    parser.add_argument("-t", "--ticker", action="store", dest="ticker", type=str, default=ticker,
                        help="ticker for which to fetch data")
    parser.add_argument("metric", type=str, action="store", default="sentiment", nargs="?",
                        choices=["sentiment", "AHI", "RHI", "SGP"], help="the metric to plot")

    ns_parser = parse_known_args_and_warn(parser, other_args)
    if not ns_parser:
        return

    data = sentipy.historical(ns_parser.ticker, ns_parser.metric, int(time.time() - 60 * 60 * 24 * 7), int(time.time()))
    df = pd.DataFrame.from_dict({
        'date': map(datetime.datetime.utcfromtimestamp, data.keys()),
        ns_parser.metric: data.values()
    })

    df.sort_index(ascending=True, inplace=True)

    if df.empty:
        print("The dataset is empty, something must have gone wrong")
        return

    _customise_plot()

    # use seaborn to lineplot
    ax = sns.lineplot(data=df, x='date', y=ns_parser.metric, legend=False)

    # always show zero on the y-axis
    plt.ylim(bottom=0)

    # set the x-axis date formatting
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%x'))

    # scale the plot appropriately
    plt.gcf().set_size_inches(plot_autoscale())
    plt.gcf().set_dpi(PLOT_DPI)
    plt.gcf().autofmt_xdate()

    # fill below the line
    plt.fill_between(df.date, df[ns_parser.metric], alpha=0.3)

    # add title e.g. AAPL sentiment since 22/07/21
    plt.title(f"{ns_parser.ticker} {ns_parser.metric} since {min(df.date).strftime('%x')}")

    plt.show()

    ###

    aggregated = df.resample('D', on='date').mean()
    aggregated.index = aggregated.index.strftime('%x')

    print(tabulate(
        aggregated,
        headers=['Day', f"average {ns_parser.metric}"],
        tablefmt='psql',
        floatfmt=".3f",
    ))
