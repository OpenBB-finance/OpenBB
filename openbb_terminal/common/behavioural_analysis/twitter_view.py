"""Twitter view."""
__docformat__ = "numpy"

import logging
import os
from typing import Optional, Union

import numpy as np
import pandas as pd
from dateutil import parser as dparse

from openbb_terminal import OpenBBFigure, theme
from openbb_terminal.common.behavioural_analysis import twitter_model
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data, get_closing_price
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_inference(
    symbol: str, limit: int = 100, export: str = "", sheet_name: Optional[str] = None
):
    """Prints Inference sentiment from past n tweets.

    Parameters
    ----------
    symbol: str
        Stock ticker symbol
    limit: int
        Number of tweets to analyze
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Format to export tweet dataframe
    """
    df_tweets = twitter_model.load_analyze_tweets(symbol, limit)

    if (isinstance(df_tweets, pd.DataFrame) and df_tweets.empty) or (
        not isinstance(df_tweets, pd.DataFrame) and not df_tweets
    ):
        return

    # Parse tweets
    dt_from = dparse.parse(df_tweets["created_at"].values[-1])
    dt_to = dparse.parse(df_tweets["created_at"].values[0])
    console.print(f"From: {dt_from.strftime('%Y-%m-%d %H:%M:%S')}")
    console.print(f"To:   {dt_to.strftime('%Y-%m-%d %H:%M:%S')}")

    console.print(f"{len(df_tweets)} tweets were analyzed.")
    dt_delta = dt_to - dt_from
    n_freq = dt_delta.total_seconds() / len(df_tweets)
    console.print(f"Frequency of approx 1 tweet every {round(n_freq)} seconds.")

    pos = df_tweets["positive"]
    neg = df_tweets["negative"]

    percent_pos = len(np.where(pos > neg)[0]) / len(df_tweets)
    percent_neg = len(np.where(pos < neg)[0]) / len(df_tweets)
    total_sent = np.round(np.sum(df_tweets["sentiment"]), 2)
    mean_sent = np.round(np.mean(df_tweets["sentiment"]), 2)
    console.print(f"The summed compound sentiment of {symbol} is: {total_sent}")
    console.print(f"The average compound sentiment of {symbol} is: {mean_sent}")
    console.print(
        f"Of the last {len(df_tweets)} tweets, {100*percent_pos:.2f} % had a higher positive sentiment"
    )
    console.print(
        f"Of the last {len(df_tweets)} tweets, {100*percent_neg:.2f} % had a higher negative sentiment"
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "infer",
        df_tweets,
        sheet_name,
    )


@log_start_end(log=logger)
def display_sentiment(
    symbol: str,
    n_tweets: int = 15,
    n_days_past: int = 2,
    compare: bool = False,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
) -> Union[OpenBBFigure, None]:
    """Plots sentiments from symbol

    Parameters
    ----------
    symbol: str
        Stock ticker symbol to get sentiment for
    n_tweets: int
        Number of tweets to get per hour
    n_days_past: int
        Number of days to extract tweets for
    compare: bool
        Show corresponding change in stock price
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Format to export tweet dataframe
    external_axes: bool, optional
        Whether to return the figure object or not, by default False
    """

    df_tweets = twitter_model.get_sentiment(symbol, n_tweets, n_days_past)

    if df_tweets.empty:
        return None

    if compare:
        plots_kwargs = dict(
            rows=3,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            row_heights=[0.2, 0.6, 0.2],
        )
    else:
        plots_kwargs = dict(
            rows=2,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            row_heights=[0.6, 0.4],
        )

    fig = OpenBBFigure.create_subplots(**plots_kwargs)  # type: ignore

    fig.add_scatter(
        x=pd.to_datetime(df_tweets["created_at"]),
        y=df_tweets["cumulative_compound"].values,
        row=1,
        col=1,
    )

    fig.set_yaxis_title("<br>Cumulative<br>VADER Sentiment", row=1, col=1)

    for _, day_df in df_tweets.groupby(by="Day"):
        day_df["time"] = pd.to_datetime(day_df["created_at"])
        day_df = day_df.sort_values(by="time")
        fig.add_scatter(
            x=day_df["time"],
            y=day_df["sentiment"].cumsum(),
            row=1,
            col=1,
        )
        fig.add_bar(
            x=df_tweets["date"],
            y=df_tweets["positive"],
            row=2,
            col=1,
            marker_color=theme.up_color,
        )

    fig.add_bar(
        x=df_tweets["date"],
        y=-1 * df_tweets["negative"],
        row=2,
        col=1,
        marker_color=theme.down_color,
    )
    fig.set_yaxis_title("VADER Polarity Scores", row=2, col=1)

    if compare:
        # get stock end price for each corresponding day if compare == True
        closing_price_df = get_closing_price(symbol, n_days_past)
        fig.add_scatter(
            x=closing_price_df["Date"],
            y=closing_price_df["Close"],
            name=pd.to_datetime(closing_price_df["Date"]).iloc[0].strftime("%Y-%m-%d"),
            row=3,
            col=1,
        )
        fig.set_yaxis_title("Stock Price", row=3, col=1)

    fig.update_layout(
        title=f"Twitter's {symbol} total compound sentiment over time is {round(np.sum(df_tweets['sentiment']), 2)}",
        xaxis=dict(type="date"),
        showlegend=False,
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "sentiment",
        df_tweets,
        sheet_name,
        fig,
    )

    return fig.show(external=external_axes)
