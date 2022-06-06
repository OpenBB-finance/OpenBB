"""Finbrain Crypto Sentiment Analysis"""
__docformat__ = "numpy"

import logging
import os
from typing import Optional, List

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

from openbb_terminal.common.behavioural_analysis.finbrain_model import get_sentiment
from openbb_terminal.common.behavioural_analysis.finbrain_view import (
    lambda_sentiment_coloring,
)
from openbb_terminal.config_terminal import theme
from openbb_terminal.decorators import log_start_end
from openbb_terminal.config_plot import PLOT_DPI
from openbb_terminal.helper_funcs import (
    export_data,
    plot_autoscale,
    is_valid_axes_count,
)
from openbb_terminal.rich_config import console
from openbb_terminal import rich_config

logger = logging.getLogger(__name__)

PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

try:
    COINS_JSON = pd.read_json(PATH + "/data/finbrain_coins.json")
    COINS = COINS_JSON["SYMBOL"].tolist()
except ValueError:
    COINS = None


@log_start_end(log=logger)
def display_crypto_sentiment_analysis(
    coin: str,
    raw: bool = False,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
) -> None:
    """Sentiment analysis from FinBrain for Cryptocurrencies

    FinBrain collects the news headlines from 15+ major financial news
    sources on a daily basis and analyzes them to generate sentiment scores
    for more than 4500 US stocks. FinBrain Technologies develops deep learning
    algorithms for financial analysis and prediction, which currently serves
    traders from more than 150 countries all around the world.
    [Source:  https://finbrain.tech]

    Parameters
    ----------
    coin: str
        Cryptocurrency
    raw : False
        Display raw table data
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """

    sentiment = get_sentiment(f"{coin}-USD")  # Currently only USD pairs are available

    if sentiment.empty:
        console.print(f"Couldn't find Sentiment Data for {coin}\n")
        return

    if not raw:
        # This plot has 1 axis
        if external_axes is None:
            _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
        elif is_valid_axes_count(external_axes, 1):
            (ax,) = external_axes
        else:
            return

        for index, row in sentiment.iterrows():
            if float(row["Sentiment Analysis"]) >= 0:
                ax.scatter(
                    index, float(row["Sentiment Analysis"]), s=100, color=theme.up_color
                )
            else:
                ax.scatter(
                    index,
                    float(row["Sentiment Analysis"]),
                    s=100,
                    color=theme.down_color,
                )
        ax.axhline(y=0, linestyle="--")
        ax.set_xlabel("Time")
        ax.set_ylabel("Finbrain's Sentiment Score")
        start_date = sentiment.index[-1].strftime("%Y/%m/%d")
        ax.set_title(f"FinBrain's Sentiment Analysis for {coin}-USD since {start_date}")
        ax.set_ylim([-1.1, 1.1])
        senValues = np.array(pd.to_numeric(sentiment["Sentiment Analysis"].values))
        senNone = np.array(0 * len(sentiment))
        ax.fill_between(
            sentiment.index,
            pd.to_numeric(sentiment["Sentiment Analysis"].values),
            0,
            where=(senValues < senNone),
            alpha=0.30,
            color=theme.down_color,
            interpolate=True,
        )
        ax.fill_between(
            sentiment.index,
            pd.to_numeric(sentiment["Sentiment Analysis"].values),
            0,
            where=(senValues >= senNone),
            alpha=0.30,
            color=theme.up_color,
            interpolate=True,
        )
        theme.style_primary_axis(ax)

        if external_axes is None:
            theme.visualize_output()

    else:
        sentiment.sort_index(ascending=True, inplace=True)

        if rich_config.USE_COLOR:
            console.print(
                sentiment["Sentiment Analysis"]
                .apply(lambda_sentiment_coloring, last_val=0)
                .to_string(),
                "\n",
            )
        else:
            console.print(sentiment.to_string(), "\n")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "finbrain",
        sentiment,
    )
