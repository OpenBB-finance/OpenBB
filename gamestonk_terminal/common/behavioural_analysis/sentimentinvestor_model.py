"""SentimentInvestor Model"""
__docformat__ = "numpy"

import dataclasses
import datetime
import logging
import multiprocessing
import os
import statistics
import time
from typing import Any, List, Optional, Tuple, Union

import pandas as pd
from colorama import Fore, Style
from sentipy.sentipy import Sentipy

from gamestonk_terminal import config_terminal as cfg

sentipy: Sentipy = Sentipy(
    token=cfg.API_SENTIMENTINVESTOR_TOKEN, key=cfg.API_SENTIMENTINVESTOR_KEY
)

# TODO: Make code more consistent with rest of repository.


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
    """Gets last 1 week average"""
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


def get_metrics(ticker: str) -> Optional[List[_Metric]]:
    """Get core metrics for ticker"""
    data = sentipy.parsed(ticker)
    return _contextualise_metrics(data, ticker, core_metrics)


def get_socials(ticker: str) -> Optional[List[_Metric]]:
    """Get social metrics for ticker"""
    data = sentipy.raw(ticker)
    return _contextualise_metrics(data, ticker, social_metrics)


def get_historical(ticker: str, metric: str) -> pd.DataFrame:
    """Get historical sentiment data [Source: sentimentinvestor]

    Parameters
    ----------
    ticker : str
        Stock
    metric : str
        Metric to get

    Returns
    -------
    pd.DataFrame
        Dataframe of historical sentiment
    """
    data = sentipy.historical(
        ticker,
        metric,
        int(time.time() - 60 * 60 * 24 * 7),
        int(time.time()),
    )
    df = pd.DataFrame.from_dict(
        {
            "date": map(datetime.datetime.utcfromtimestamp, data.keys()),
            metric: data.values(),
        }
    )

    df.sort_index(ascending=True, inplace=True)
    return df


def get_top(metric: str, limit: int) -> List[List[Any]]:
    """Get top stocks based on metric from sentimentinvestor [Source: sentimentinvestor]

    Parameters
    ----------
    metric : str
        Metric to get top tickers for
    limit : int
        Number of tickes to get

    Returns
    -------
    List[List[Any]]
        List of tickers and scores
    """
    data = sentipy.sort(metric, limit)

    table: List[List[Any]] = []
    for index, stock in enumerate(data):
        if not hasattr(stock, "symbol") or not hasattr(stock, metric):
            logging.warning("data for stock %s is incomplete, ignoring", index + 1)
            table.append([])
        else:
            table.append([index + 1, stock.symbol, stock.__getattribute__(metric)])
    return table
