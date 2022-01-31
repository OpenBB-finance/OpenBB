""" Quandl View """
__docformat__ = "numpy"

import logging
import os

import matplotlib.ticker
import pandas as pd
from matplotlib import pyplot as plt

from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.helper_funcs import (
    export_data,
    long_number_format,
    print_rich_table,
)
from gamestonk_terminal.rich_config import console
from gamestonk_terminal.stocks.dark_pool_shorts import quandl_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def plot_short_interest(ticker: str, nyse: bool, df_short_interest: pd.DataFrame):
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
    df_short_interest: pd.DataFrame
        Short interest dataframe
    """
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
    ax.set_title(f"{('NASDAQ', 'NYSE')[nyse]} Short Interest on {ticker}")

    ax.legend(labels=["Short Volume", "Total Volume"], loc="best")
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
    plt.gcf().autofmt_xdate()

    if gtff.USE_ION:
        plt.ion()

    plt.show()


@log_start_end(log=logger)
def short_interest(ticker: str, nyse: bool, days: int, raw: bool, export: str):
    """Plots the short interest of a stock. This corresponds to the
    number of shares that have been sold short but have not yet been
    covered or closed out. Either NASDAQ or NYSE [Source: Quandl]

    Parameters
    ----------
    ticker : str
        ticker to get short interest from
    nyse : bool
        data from NYSE if true, otherwise NASDAQ
    days : int
        Number of past days to show short interest
    raw : bool
        Flag to print raw data instead
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    df_short_interest = quandl_model.get_short_interest(ticker, nyse)

    df_short_interest = df_short_interest.tail(days)

    df_short_interest.columns = [
        "".join(" " + char if char.isupper() else char.strip() for char in idx).strip()
        for idx in df_short_interest.columns.tolist()
    ]
    pd.options.mode.chained_assignment = None
    vol_pct = (
        100
        * df_short_interest["Short Volume"].values
        / df_short_interest["Total Volume"].values
    )
    df_short_interest["% of Volume Shorted"] = [round(pct, 2) for pct in vol_pct]

    if raw:
        df_short_interest["% of Volume Shorted"] = df_short_interest[
            "% of Volume Shorted"
        ].apply(lambda x: f"{x/100:.2%}")
        df_short_interest = df_short_interest.applymap(
            lambda x: long_number_format(x)
        ).sort_index(ascending=False)

        df_short_interest.index = df_short_interest.index.date

        print_rich_table(
            df_short_interest,
            headers=list(df_short_interest.columns),
            show_index=True,
            title="Short Interest of Stock",
        )

    console.print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "psi(quandl)",
        df_short_interest,
    )
