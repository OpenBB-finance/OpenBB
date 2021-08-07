import argparse
import dataclasses
import datetime
import logging
import multiprocessing
import os
import statistics
import textwrap
import time
from typing import Union, Optional, List, Tuple

import matplotlib.dates as mdates
import pandas as pd
import seaborn as sns
from colorama import Fore, Style
from matplotlib import pyplot as plt
from sentipy.sentipy import Sentipy
import tabulate

from gamestonk_terminal import config_terminal as cfg
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.helper_funcs import (
    parse_known_args_and_warn,
    plot_autoscale,
)

sentipy: Sentipy = Sentipy(
    token=cfg.API_SENTIMENTINVESTOR_TOKEN, key=cfg.API_SENTIMENTINVESTOR_KEY
)
"""Initialise SentiPy with the user's API token and key"""

pd.plotting.register_matplotlib_converters()


# suppress warning messages for a clean interface
logging.getLogger().setLevel(logging.CRITICAL)


@dataclasses.dataclass
class _Boundary:
    """Represents a strong or weak bounding inequality for categorising a value"""

    min: Union[float, int]
    "Minimum value that this metric could take"
    max: Union[float, int]
    "Maximum value that this metric could take"
    strong: bool = False
    "Whether this a strongly bounded inequality"

    def categorise(self, num: Union[float, int]) -> Tuple[str, str]:
        """
        Categorise a given number using this bounding inequality

        Parameters
        ----------
        num: the number to bucket

        Returns
        -------
        A color string and a string with low / medium / high as appropriate

        """

        if num is None or self.min is None or self.max is None:
            return Style.DIM + Fore.WHITE, "N/A"

        boundaries = [self.min + (self.max - self.min) / 5 * i for i in range(1, 5)]

        if (num <= self.min or num >= self.max) and self.strong:
            return Fore.WHITE, "Extreme (anomaly?)"
        if num < boundaries[0]:
            return Style.BRIGHT + Fore.RED, "Much Lower"
        if num < boundaries[1]:
            return Fore.RED, "Lower"
        if num < boundaries[2]:
            return Fore.YELLOW, "Same"
        if num < boundaries[3]:
            return Fore.GREEN, "Higher"
        return Style.BRIGHT + Fore.GREEN, "Much Higher"


def _get_past_week_average(ticker: str, metric: str) -> float:
    historical_data = [
        dp
        for dp in sentipy.historical(
            ticker, metric, int(time.time() - 60 * 60 * 24 * 7), int(time.time())
        ).values()
        if dp is not None
    ]
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

    def __init__(
        self,
        metric_info: _MetricInfo,
        ticker: str,
        value: Union[float, int],
        boundary: Optional[_Boundary] = None,
    ):
        super().__init__(**dataclasses.asdict(metric_info))

        weekly_mean = _get_past_week_average(ticker, self.name)
        self.boundary = (
            _Boundary(0, None if weekly_mean is None else 2 * weekly_mean)
            if boundary is None
            else boundary
        )
        self.ticker = ticker
        self.value = value

    def visualise(self) -> Tuple[str, str, str, str]:
        color, category = self.boundary.categorise(self.value)
        return (
            color + self.title,
            category,
            "N/A" if self.value is None else f"{self.value:{self.format}}",
            self.description + Style.RESET_ALL,
        )


core_metrics = [
    _MetricInfo(
        "sentiment",
        "Sentiment Score",
        "the percentage of people that are talking positively about a stock",
        ".0%",
    ),
    _MetricInfo(
        "AHI",
        "Average Hype Index",
        "how much people are talking about a stock on social media",
        ".3f",
    ),
    _MetricInfo(
        "RHI",
        "Relative Hype Index",
        "whether people are talking about a stock more or less than usual",
        ".3f",
    ),
    _MetricInfo(
        "SGP",
        "Standard General Perception",
        "whether people are more or less positive about a stock than usual",
        ".3f",
    ),
]

social_metrics = [
    _MetricInfo(
        "reddit_comment_mentions",
        "Reddit Comment Mentions",
        "the number of mentions this stock has received in Reddit comments",
        "n",
    ),
    _MetricInfo(
        "reddit_comment_sentiment",
        "Reddit Comment Sentiment",
        "percentage of Reddit comments mentioning this stock in a positive light",
        ".0%",
    ),
    _MetricInfo(
        "reddit_post_mentions",
        "Reddit Post Mentions",
        "the number of mentions this stock has received in Reddit posts",
        "n",
    ),
    _MetricInfo(
        "reddit_post_sentiment",
        "Reddit Post Sentiment",
        "percentage of Reddit posts mentioning this stock in a positive light",
        ".0%",
    ),
    _MetricInfo(
        "tweet_mentions",
        "Twitter Mentions",
        "the number of mentions this stock has received on Twitter",
        "n",
    ),
    _MetricInfo(
        "tweet_sentiment",
        "Twitter Sentiment",
        "percentage of tweets mentioning this stock in a positive light",
        ".0%",
    ),
    _MetricInfo(
        "stocktwits_post_mentions",
        "Stocktwits Mentions",
        "the number of mentions this stock has received in Stocktwits posts",
        "n",
    ),
    _MetricInfo(
        "stocktwits_post_sentiment",
        "Stocktwits Sentiment",
        "percentage of Stocktwits posts mentioning this stock in a positive light",
        ".0%",
    ),
    _MetricInfo(
        "yahoo_finance_comment_mentions",
        "Yahoo! Finance Comment Mentions",
        "the number of mentions this stock has received in Yahoo! Finance comments",
        "n",
    ),
    _MetricInfo(
        "yahoo_finance_comment_sentiment",
        "Yahoo! Finance Comment Sentiment",
        "percentage of Yahoo! Finance comments mentioning this stock in a positive light",
        ".0%",
    ),
]


def _contextualise_metrics(
    data: object, ticker: str, metric_infos: List[_MetricInfo]
) -> Optional[List[_Metric]]:
    arguments = []
    for metric_info in metric_infos:
        if not hasattr(data, metric_info.name):
            logging.error(
                "data for %s stock is incomplete. If you believe this is an error, "
                "please contact hello@sentimentinvestor.com",
                ticker,
            )
            return None
        arguments.append((metric_info, ticker, data.__getattribute__(metric_info.name)))

    with multiprocessing.Pool(os.cpu_count()) as pool:
        return pool.starmap(_Metric, arguments)


def _tabulate_metrics(ticker: str, metrics_list: List[_Metric]):
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


def _parse_args_for_ticker(other_args: List[str], ticker: str, command: str, desc: str):
    parser = argparse.ArgumentParser(
        add_help=False,
        prog=command,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=desc,
    )

    parser.add_argument(
        "ticker",
        action="store",
        type=str,
        nargs="?",
        default=ticker,
        help="ticker to use instead of the loaded one",
    )

    return parse_known_args_and_warn(parser, other_args)


def metrics(ticker: str, other_args: List[str]) -> None:
    command_description = f"""
        {Style.BRIGHT}Sentiment Investor{Style.RESET_ALL} analyzes data from four major social media platforms to
        generate hourly metrics on over 2,000 stocks. Sentiment provides volume and
        sentiment metrics powered by proprietary NLP models.

        The {Style.BRIGHT}metrics{Style.RESET_ALL} command prints the following realtime metrics:

        {Style.BRIGHT}AHI (Absolute Hype Index){Style.RESET_ALL}
        ---
        AHI is a measure of how much people are talking about a stock on social media.
        It is calculated by dividing the total number of mentions for the chosen stock
        on a social network by the mean number of mentions any stock receives on that
        social medium.

        {Style.BRIGHT}RHI (Relative Hype Index){Style.RESET_ALL}
        ---
        RHI is a measure of whether people are talking about a stock more or less than
        usual, calculated by dividing the mean AHI for the past day by the mean AHI for
        for the past week for that stock.

        {Style.BRIGHT}Sentiment Score{Style.RESET_ALL}
        ---
        Sentiment score is the percentage of people talking positively about the stock.
        For each social network the number of positive posts/comments is divided by the
        total number of both positive and negative posts/comments.

        {Style.BRIGHT}SGP (Standard General Perception){Style.RESET_ALL}
        ---
        SGP is a measure of whether people are more or less positive about a stock than
        usual. It is calculated by averaging the past day of sentiment values and then
        dividing it by the average of the past week of sentiment values.
        """

    ns_parser = _parse_args_for_ticker(
        other_args=other_args,
        ticker=ticker,
        command="metrics",
        desc=textwrap.dedent(command_description),
    )

    try:

        if not ns_parser:
            logging.error("There was an error in parsing the command-line arguments.")
            return

        if not sentipy.supported(ns_parser.ticker):
            print("This stock is not supported by the SentimentInvestor API.")
            return

        data = sentipy.parsed(ns_parser.ticker)

        metric_values = _contextualise_metrics(data, ns_parser.ticker, core_metrics)

        if not metric_values:
            logging.error("No data available or an error occurred.")
            return

        print(_tabulate_metrics(ns_parser.ticker, metric_values))
        print()

    except Exception as e:
        logging.error(e)
        print(e, "\n")


def socials(ticker: str, other_args: List[str]) -> None:
    command_description = f"""
        {Style.BRIGHT}Sentiment Investor{Style.RESET_ALL} analyzes data from four major social media platforms to
        generate hourly metrics on over 2,000 stocks. Sentiment provides volume and
        sentiment metrics powered by proprietary NLP models.

        The {Style.BRIGHT}social{Style.RESET_ALL} command prints the raw data for a given stock, including the number
        of mentions it has received on social media in the last hour and the sentiment
        score of those comments.
        """

    try:

        ns_parser = _parse_args_for_ticker(
            other_args=other_args,
            ticker=ticker,
            command="social",
            desc=textwrap.dedent(command_description),
        )

        if not ns_parser:
            logging.error("There was an error in parsing the command-line arguments.")
            return

        if not sentipy.supported(ns_parser.ticker):
            print("This stock is not supported by the SentimentInvestor API.")
            return

        data = sentipy.raw(ns_parser.ticker)

        metric_values = _contextualise_metrics(data, ns_parser.ticker, social_metrics)

        if not metric_values:
            logging.error("No data available or an error occurred.")
            return

        print(_tabulate_metrics(ns_parser.ticker, metric_values))
        print()

    except Exception as e:
        logging.error(e)
        print(e, "\n")


def historical(ticker: str, other_args: List[str]) -> None:
    command_description = f"""
        {Style.BRIGHT}Sentiment Investor{Style.RESET_ALL} analyzes data from four major social media platforms to
        generate hourly metrics on over 2,000 stocks. Sentiment provides volume and
        sentiment metrics powered by proprietary NLP models.

        The {Style.BRIGHT}historical{Style.RESET_ALL} command plots the past week of data for a selected metric, one of:

        {Style.BRIGHT}AHI (Absolute Hype Index){Style.RESET_ALL}
        ---
        AHI is a measure of how much people are talking about a stock on social media.
        It is calculated by dividing the total number of mentions for the chosen stock
        on a social network by the mean number of mentions any stock receives on that
        social medium.

        {Style.BRIGHT}RHI (Relative Hype Index){Style.RESET_ALL}
        ---
        RHI is a measure of whether people are talking about a stock more or less than
        usual, calculated by dividing the mean AHI for the past day by the mean AHI for
        for the past week for that stock.

        {Style.BRIGHT}Sentiment Score{Style.RESET_ALL}
        ---
        Sentiment score is the percentage of people talking positively about the stock.
        For each social network the number of positive posts/comments is divided by the
        total number of both positive and negative posts/comments.

        {Style.BRIGHT}SGP (Standard General Perception){Style.RESET_ALL}
        ---
        SGP is a measure of whether people are more or less positive about a stock than
        usual. It is calculated by averaging the past day of sentiment values and then
        dividing it by the average of the past week of sentiment values.
        """

    parser = argparse.ArgumentParser(
        add_help=False,
        prog="historical",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent(command_description),
    )
    parser.add_argument(
        "-t",
        "--ticker",
        action="store",
        dest="ticker",
        type=str,
        default=ticker,
        help="ticker for which to fetch data",
    )
    parser.add_argument(
        "-s",
        "--sort",
        action="store",
        type=str,
        default="date",
        help="the parameter to sort output table by",
        dest="sort_param",
        nargs="?",
        choices=["date", "value"],
    )
    parser.add_argument(
        "-d",
        "--direction",
        action="store",
        type=str,
        default="desc",
        help="the direction to sort the output table",
        dest="sort_dir",
        nargs="?",
        choices=["asc", "desc"],
    )
    parser.add_argument(
        "metric",
        type=str,
        action="store",
        default="sentiment",
        nargs="?",
        choices=["sentiment", "AHI", "RHI", "SGP"],
        help="the metric to plot",
    )

    try:

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            logging.error("There was an error in parsing the command-line arguments.")
            return

        if not sentipy.supported(ns_parser.ticker):
            print("This stock is not supported by the SentimentInvestor API.")
            return

        data = sentipy.historical(
            ns_parser.ticker,
            ns_parser.metric,
            int(time.time() - 60 * 60 * 24 * 7),
            int(time.time()),
        )
        df = pd.DataFrame.from_dict(
            {
                "date": map(datetime.datetime.utcfromtimestamp, data.keys()),
                ns_parser.metric: data.values(),
            }
        )

        df.sort_index(ascending=True, inplace=True)

        if df.empty:
            logging.error("The dataset is empty, something must have gone wrong")
            return

        _customise_plot()

        # use seaborn to lineplot
        ax = sns.lineplot(
            data=df,
            x="date",
            y=ns_parser.metric,
            legend=False,
            label=[ns_parser.metric],
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
        plt.fill_between(df.date, df[ns_parser.metric], alpha=0.3)

        # add title e.g. AAPL sentiment since 22/07/21
        plt.title(
            f"{ns_parser.ticker} {ns_parser.metric} since {min(df.date).strftime('%x')}"
        )

        plt.show()

        ###

        boundary = _Boundary(
            0, max(df[ns_parser.metric].max(), 2 * df[ns_parser.metric].mean())
        )

        # average for each day
        aggregated = df.resample("D", on="date").mean()

        # reverse the ordering if requested
        aggregated.sort_values(
            ns_parser.metric
            if ns_parser.sort_param == "value"
            else ns_parser.sort_param,
            axis=0,
            ascending=ns_parser.sort_dir == "asc",
            inplace=True,
        )

        # format the date according to user's locale
        aggregated.index = aggregated.index.strftime("%x")

        # apply coloring to every value
        aggregated[ns_parser.metric] = [
            boundary.categorise(value)[0] + str(value) + Style.RESET_ALL
            for value in aggregated[ns_parser.metric]
        ]

        print(
            tabulate.tabulate(
                aggregated,
                headers=["Day", f"average {ns_parser.metric}"],
                tablefmt="psql",
                floatfmt=".3f",
            )
        )
        print()

    except Exception as e:
        logging.error(e)
        print(e, "\n")
