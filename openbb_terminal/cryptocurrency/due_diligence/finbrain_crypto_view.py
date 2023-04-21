"""Finbrain Crypto Sentiment Analysis"""
__docformat__ = "numpy"

import logging
import os
from typing import Optional, Union

import numpy as np
import pandas as pd

from openbb_terminal import OpenBBFigure, rich_config, theme
from openbb_terminal.common.behavioural_analysis.finbrain_model import get_sentiment
from openbb_terminal.common.behavioural_analysis.finbrain_view import (
    lambda_sentiment_coloring,
)
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)

PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

try:
    COINS_JSON = pd.read_json(PATH + "/data/finbrain_coins.json")
    COINS = COINS_JSON["SYMBOL"].tolist()
except ValueError:
    COINS = None


@log_start_end(log=logger)
def display_crypto_sentiment_analysis(
    symbol: str,
    raw: bool = False,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
) -> Union[None, OpenBBFigure]:
    """Sentiment analysis from FinBrain for Cryptocurrencies

    FinBrain collects the news headlines from 15+ major financial news
    sources on a daily basis and analyzes them to generate sentiment scores
    for more than 4500 US stocks. FinBrain Technologies develops deep learning
    algorithms for financial analysis and prediction, which currently serves
    traders from more than 150 countries all around the world.
    [Source:  https://finbrain.tech]

    Parameters
    ----------
    symbol: str
        Cryptocurrency
    raw : False
        Display raw table data
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    fig = OpenBBFigure()

    sentiment = get_sentiment(f"{symbol}-USD")  # Currently only USD pairs are available

    if sentiment.empty:
        return console.print(f"Couldn't find Sentiment Data for {symbol}\n")

    if not fig.is_image_export(export):
        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "finbrain",
            sentiment,
            sheet_name,
        )

    if raw and not fig.is_image_export(export):
        sentiment.sort_index(ascending=True, inplace=True)

        if rich_config.USE_COLOR:
            return console.print(
                sentiment["Sentiment Analysis"]
                .apply(lambda_sentiment_coloring, last_val=0)
                .to_string(),
                "\n",
            )

        return console.print(sentiment.to_string(), "\n")

    start_date = sentiment.index[0].strftime("%Y/%m/%d")

    fig = OpenBBFigure(xaxis_title="Time", yaxis_title="Finbrain's Sentiment Score")
    fig.set_title(f"FinBrain's Sentiment Analysis for {symbol}-USD since {start_date}")

    senValues = np.array(pd.to_numeric(sentiment["Sentiment Analysis"].values))
    senNone = np.array(0 * len(sentiment))
    df_sentiment = sentiment["Sentiment Analysis"]
    negative_yloc = np.where(senValues < senNone)[0]
    positive_yloc = np.where(senValues > senNone)[0]

    fig.add_scatter(
        x=df_sentiment.index[positive_yloc],
        y=pd.to_numeric(df_sentiment.values)[positive_yloc],
        marker=dict(color=theme.up_color, size=10),
        mode="lines+markers",
        line_width=0,
        name=symbol,
    )
    fig.add_scatter(
        x=[df_sentiment.index[0], df_sentiment.index[-1]],
        y=[0, 0],
        fillcolor=theme.up_color,
        line=dict(color="white", dash="dash"),
        fill="tonexty",
        mode="lines",
        name=symbol,
    )
    fig.add_scatter(
        x=df_sentiment.index[negative_yloc],
        y=pd.to_numeric(df_sentiment.values)[negative_yloc],
        fill="tonexty",
        fillcolor=theme.down_color,
        marker=dict(color=theme.down_color, size=10),
        line_width=0,
        mode="lines+markers",
        name=symbol,
    )
    fig.update_traces(showlegend=False)

    if fig.is_image_export(export):
        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "finbrain",
            sentiment,
            sheet_name,
            fig,
        )

    return fig.show(external=raw or external_axes)
