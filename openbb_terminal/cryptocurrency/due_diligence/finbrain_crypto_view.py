"""Finbrain Crypto Sentiment Analysis"""
__docformat__ = "numpy"

import logging
import os

import pandas as pd

from openbb_terminal.common.behavioural_analysis.finbrain_model import get_sentiment
from openbb_terminal.common.behavioural_analysis.finbrain_view import (
    plot_sentiment,
    lambda_sentiment_coloring,
)
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data
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
def display_crypto_sentiment_analysis(coin: str, export: str) -> None:
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
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df_sentiment = get_sentiment(
        f"{coin}-USD"
    )  # Currently only USD pairs are available

    if df_sentiment.empty:
        console.print(f"Couldn't find Sentiment Data for {coin}\n")
        return

    plot_sentiment(df_sentiment, coin)
    df_sentiment.sort_index(ascending=True, inplace=True)

    if rich_config.USE_COLOR:
        console.print(
            df_sentiment["Sentiment Analysis"]
            .apply(lambda_sentiment_coloring, last_val=0)
            .to_string(),
            "\n",
        )
    else:
        console.print(df_sentiment.to_string(), "\n")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "finbrain",
        df_sentiment,
    )
