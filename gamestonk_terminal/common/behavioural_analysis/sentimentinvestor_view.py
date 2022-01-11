"""SentimentInvestor View"""
__docformat__ = "numpy"

import matplotlib.dates as mdates
from numpy import str0
import pandas as pd
from matplotlib import pyplot as plt
import os

from gamestonk_terminal.common.behavioural_analysis import sentimentinvestor_model
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import export_data


def display_historical(ticker: str, start: str, end: str, limit: int, export: str):
    """Display historical sentiment data of a ticker,
    and plot a chart with RHI and AHI.

    Parameters
    ----------
    ticker: str
        Ticker to view sentiment data
    start: str
        Initial date like string or unix timestamp (e.g. 12-21-2021)
    end: str
        End date like string or unix timestamp (e.g. 12-21-2021)
    limit : int
        Limit number of results
        Maximum 250 per api call

    Returns
    -------
    """


    df = sentimentinvestor_model.get_historical(ticker, start, end, limit)

    if df.empty:
        print("Error in Sentiment Investor request")
    else:
        _, ax1 = plt.subplots(figsize=(25, 7))
        ax1.plot(df.index, df["RHI"], c="k")
        ax2 = ax1.twinx()

        ax1.grid()
        ax2.plot(df.index, df["AHI"], c="orange")

        ax1.set_ylabel(f"RHI")
        ax1.set_xlabel("Time")
        ax1.set_title(
            f"Hourly-level data of RHI and AHI"
        )
        ax1.set_xlim(df.index[0], df.index[-1])
        ax2.set_ylabel(f"AHI")

        interval_locator = mdates.HourLocator(interval=6)
        plt.gca().xaxis.set_major_locator(interval_locator)
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d %H:%M"))
        plt.gcf().autofmt_xdate()

        if gtff.USE_ION:
            plt.ion()

        plt.show()

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "his",
            df,
        )
