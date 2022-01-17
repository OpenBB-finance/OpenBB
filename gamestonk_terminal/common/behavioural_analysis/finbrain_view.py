"""FinBrain View Module"""
__docformat__ = "numpy"

import os
from matplotlib import pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
from pandas.plotting import register_matplotlib_converters
import numpy as np
from tabulate import tabulate
from gamestonk_terminal.helper_funcs import plot_autoscale, export_data
from gamestonk_terminal.common.behavioural_analysis import finbrain_model
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.rich_config import console


register_matplotlib_converters()


def sentiment_coloring(val: float, last_val: float) -> str:
    if float(val) > last_val:
        return f"[green]{val}[/green]"
    return f"[red]{val}[/red]"


def plot_sentiment(sentiment: pd.DataFrame, ticker: str) -> None:
    """Plot Sentiment analysis provided by FinBrain's API

    Parameters
    ----------
    sentiment : pd.DataFrame
        Dataframe with sentiment data to plot
    ticker : str
        Ticker to get the sentiment analysis from
    """
    fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    for index, row in sentiment.iterrows():
        if float(row["Sentiment Analysis"]) >= 0:
            ax.scatter(index, float(row["Sentiment Analysis"]), s=100, c="green")
        else:
            ax.scatter(index, float(row["Sentiment Analysis"]), s=100, c="red")
    ax.axhline(y=0, color="k", linestyle="--", lw=2)
    ax.set_xlabel("Time")
    ax.set_ylabel("Sentiment")
    ax.grid(b=True, which="major", color="#666666", linestyle="-")
    ax.minorticks_on()
    ax.grid(b=True, which="minor", color="#999999", linestyle="-", alpha=0.2)
    start_date = sentiment.index[-1].strftime("%Y/%m/%d")
    ax.set_title(
        f"FinBrain's Sentiment Analysis for {ticker.upper()} since {start_date}"
    )
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y/%m/%d"))
    plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=1))
    plt.gcf().autofmt_xdate()
    ax.set_ylim([-1.1, 1.1])
    senValues = np.array(pd.to_numeric(sentiment["Sentiment Analysis"].values))
    senNone = np.array(0 * len(sentiment))
    ax.fill_between(
        sentiment.index,
        pd.to_numeric(sentiment["Sentiment Analysis"].values),
        0,
        where=(senValues < senNone),
        alpha=0.30,
        color="red",
        interpolate=True,
    )
    ax.fill_between(
        sentiment.index,
        pd.to_numeric(sentiment["Sentiment Analysis"].values),
        0,
        where=(senValues >= senNone),
        alpha=0.30,
        color="green",
        interpolate=True,
    )
    if gtff.USE_ION:
        plt.ion()
    fig.tight_layout()
    plt.show()


def display_sentiment_analysis(ticker: str, export: str = ""):
    """Sentiment analysis from FinBrain

    Parameters
    ----------
    ticker : str
        Ticker to get the sentiment analysis from
    export : str
        Format to export data
    """
    df_sentiment = finbrain_model.get_sentiment(ticker)
    if df_sentiment.empty:
        console.print("No sentiment data found.\n")
        return

    plot_sentiment(df_sentiment, ticker)

    df_sentiment.sort_index(ascending=True, inplace=True)

    if gtff.USE_COLOR:
        color_df = df_sentiment["Sentiment Analysis"].apply(
            sentiment_coloring, last_val=0
        )
        if gtff.USE_TABULATE_DF:
            color_df = pd.DataFrame(
                data=color_df.values,
                index=pd.to_datetime(df_sentiment.index).strftime("%Y-%m-%d"),
            )
            print(tabulate(color_df, headers=["Sentiment"], tablefmt="fancy_grid"))
        else:
            console.print(color_df.to_string())
    else:
        if gtff.USE_TABULATE_DF:
            print(
                tabulate(
                    pd.DataFrame(
                        data=df_sentiment.values,
                        index=pd.to_datetime(df_sentiment.index).strftime("%Y-%m-%d"),
                    ),
                    headers=["Sentiment"],
                    tablefmt="fancy_grid",
                )
            )

        else:
            console.print(df_sentiment.to_string())
    console.print("")
    export_data(
        export, os.path.dirname(os.path.abspath(__file__)), "headlines", df_sentiment
    )
