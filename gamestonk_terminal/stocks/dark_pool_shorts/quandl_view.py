""" Quandl View """
__docformat__ = "numpy"

import os
import matplotlib.ticker
from matplotlib import pyplot as plt
import pandas as pd
from gamestonk_terminal.stocks.dark_pool_shorts import quandl_model
from gamestonk_terminal.helper_funcs import (
    long_number_format,
    export_data,
)


def plot_short_interest(
    ticker: str, start: str, nyse: bool, days: int, df_short_interest: pd.DataFrame
):
    """Plots the short interest of a stock. This corresponds to the
    number of shares that have been sold short but have not yet been
    covered or closed out. Either NASDAQ or NYSE [Source: Quandl]

    Parameters
    ----------
    ticker : str
        ticker to get short interest from
    start : str
        start date to start displaying short interest volume
    nyse : bool
        data from NYSE if true, otherwise NASDAQ
    days : int
        Number of past days to show short interest
    df_short_interest: pd.DataFrame
        Short interest dataframe
    """
    df_short_interest = df_short_interest[start:]  # type: ignore
    df_short_interest.columns = [
        "".join(" " + char if char.isupper() else char.strip() for char in idx).strip()
        for idx in df_short_interest.columns.tolist()
    ]
    df_short_interest["% of Volume Shorted"] = round(
        100 * df_short_interest["Short Volume"] / df_short_interest["Total Volume"],
        2,
    )

    _, ax = plt.subplots()
    ax.bar(df_short_interest.index, df_short_interest["Short Volume"], 0.3, color="r")
    ax.bar(
        df_short_interest.index,
        df_short_interest["Total Volume"] - df_short_interest["Short Volume"],
        0.3,
        bottom=df_short_interest["Short Volume"],
        color="b",
    )
    ax.set_ylabel("Shares")
    ax.set_xlabel("Date")

    if start:
        ax.set_title(
            f"{('NASDAQ', 'NYSE')[nyse]} Short Interest on {ticker} from {start.date()}"  # type: ignore
        )
    else:
        ax.set_title(f"{('NASDAQ', 'NYSE')[nyse]} Short Interest on {ticker}")

    ax.legend(labels=["Short Volume", "Total Volume"])
    ax.tick_params(axis="both", which="major")
    ax.yaxis.set_major_formatter(matplotlib.ticker.EngFormatter())
    ax_twin = ax.twinx()
    ax_twin.tick_params(axis="y", colors="green")
    ax_twin.set_ylabel("Percentage of Volume Shorted", color="green")
    ax_twin.plot(
        df_short_interest.index,
        df_short_interest["% of Volume Shorted"],
        color="green",
    )
    ax_twin.tick_params(axis="y", which="major", color="green")
    ax_twin.yaxis.set_major_formatter(matplotlib.ticker.FormatStrFormatter("%.0f%%"))
    plt.xlim([df_short_interest.index[0], df_short_interest.index[-1]])

    df_short_interest["% of Volume Shorted"] = df_short_interest[
        "% of Volume Shorted"
    ].apply(lambda x: f"{x/100:.2%}")
    df_short_interest = df_short_interest.applymap(
        lambda x: long_number_format(x)
    ).sort_index(ascending=False)

    pd.set_option("display.max_colwidth", 70)
    print(df_short_interest.head(n=days).to_string())
    print("")
    plt.show()


def short_interest(ticker: str, start: str, nyse: bool, days: int, export: str):
    """Plots the short interest of a stock. This corresponds to the
    number of shares that have been sold short but have not yet been
    covered or closed out. Either NASDAQ or NYSE [Source: Quandl]

    Parameters
    ----------
    ticker : str
        ticker to get short interest from
    start : str
        start date to start displaying short interest volume
    nyse : bool
        data from NYSE if true, otherwise NASDAQ
    days : int
        Number of past days to show short interest
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    df_short_interest = quandl_model.get_short_interest(ticker, nyse)

    plot_short_interest(ticker, start, nyse, days, df_short_interest)

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "shortint(quandl)",
        df_short_interest,
    )
