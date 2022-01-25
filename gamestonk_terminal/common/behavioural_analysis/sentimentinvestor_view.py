"""SentimentInvestor View"""
__docformat__ = "numpy"

import os
import matplotlib.dates as mdates
from matplotlib import pyplot as plt

from gamestonk_terminal.common.behavioural_analysis import sentimentinvestor_model
from gamestonk_terminal.helper_funcs import export_data, print_rich_table
from gamestonk_terminal import feature_flags as gtff

# pylint: disable=E1101


def display_historical(
    ticker: str,
    start: str,
    end: str,
    export: str,
    number: int = 100,
    raw: bool = True,
    limit: int = 10,
):
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
    number : int
        Number of results returned by API call
        Maximum 250 per api call
    raw: boolean
        Whether to display raw data, by default True
    limit: int
        Number of results display on the terminal
        Default: 10
    Returns
    -------
    """

    df = sentimentinvestor_model.get_historical(ticker, start, end, number)

    if df.empty:
        print("Error in Sentiment Investor request")
    else:
        _, ax1 = plt.subplots(figsize=(25, 7))
        ax1.plot(df.index, df["RHI"], c="k")
        ax2 = ax1.twinx()

        ax1.grid()
        ax2.plot(df.index, df["AHI"], c="orange")

        ax1.set_ylabel("RHI")
        ax1.set_xlabel("Time")
        ax1.set_title("Hourly-level data of RHI and AHI")
        ax1.set_xlim(df.index[0], df.index[-1])
        ax2.set_ylabel("AHI")

        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d %H:%M"))
        plt.gcf().autofmt_xdate()

        if gtff.USE_ION:
            plt.ion()

        plt.show()

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
            "hist",
            df,
        )

        RAW_COLS = ["twitter", "stocktwits", "yahoo", "likes", "RHI", "AHI"]

        if raw:
            df.index = df.index.strftime("%Y-%m-%d %H:%M")
            df.index.name = "Time"

            print_rich_table(
                df[RAW_COLS].head(limit),
                headers=[
                    "Time",
                    "Twitter",
                    "Stocktwits",
                    "Yahoo",
                    "Likes",
                    "RHI",
                    "AHI",
                ],
                show_index=True,
                title="Historical Sentiment Data",
            )
