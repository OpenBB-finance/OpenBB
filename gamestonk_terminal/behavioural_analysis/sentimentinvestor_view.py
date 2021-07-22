import dataclasses
import statistics
import time
from typing import Union, Optional

from colorama import Fore, Style
from sentipy.sentipy import Sentipy
from tabulate import tabulate

from gamestonk_terminal import config_terminal as cfg

sentipy: Sentipy = Sentipy(
    token=cfg.API_SENTIMENTINVESTOR_TOKEN, key=cfg.API_SENTIMENTINVESTOR_KEY)
"""Initialise SentiPy with the user's API token and key"""


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


def metrics(ticker: str, other_args: list[str]) -> None:
    data = sentipy.parsed(ticker)
    metric_values = [_Metric(metric_info, ticker, data.__getattribute__(metric_info.name)) for metric_info in
                     core_metrics]

    print(_tabulate_metrics(ticker, metric_values))


def socials(ticker: str, other_args: list[str]) -> None:
    data = sentipy.raw(ticker)
    metric_values = [_Metric(metric_info, ticker, data.__getattribute__(metric_info.name)) for metric_info in
                     social_metrics]

    print(_tabulate_metrics(ticker, metric_values))
