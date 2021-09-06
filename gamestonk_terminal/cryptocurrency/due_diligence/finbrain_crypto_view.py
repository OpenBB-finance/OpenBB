"""Finbrain Crypto Sentiment Analysis"""
__docformat__ = "numpy"

import os
import pandas as pd
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.common.behavioural_analysis.finbrain_view import (
    get_sentiment,
    plot_sentiment,
    sentiment_coloring,
)
from gamestonk_terminal.helper_funcs import export_data

PATH = os.path.dirname(os.path.abspath(__file__))

try:
    COINS_JSON = pd.read_json(PATH + "/data/finbrain_coins.json")
    COINS = COINS_JSON["SYMBOL"].tolist()
except ValueError:
    COINS = None


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
        print(f"Couldn't find Sentiment Data for {coin}\n")
        return

    plot_sentiment(df_sentiment, coin)
    df_sentiment.sort_index(ascending=True, inplace=True)

    if gtff.USE_COLOR:
        print(
            df_sentiment["Sentiment Analysis"]
            .apply(sentiment_coloring, last_val=0)
            .to_string(),
            "\n",
        )
    else:
        print(df_sentiment.to_string(), "\n")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "finbrain",
        df_sentiment,
    )
