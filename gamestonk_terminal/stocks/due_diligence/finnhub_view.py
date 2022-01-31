""" Finnhub View """
__docformat__ = "numpy"

import logging
import os

import pandas as pd
from matplotlib import pyplot as plt
from pandas.plotting import register_matplotlib_converters

from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.helper_funcs import (
    export_data,
    plot_autoscale,
    print_rich_table,
)
from gamestonk_terminal.rich_config import console
from gamestonk_terminal.stocks.due_diligence import finnhub_model

logger = logging.getLogger(__name__)

register_matplotlib_converters()


@log_start_end(log=logger)
def plot_rating_over_time(df_rot: pd.DataFrame, ticker: str):
    """Plot rating over time

    Parameters
    ----------
    df_rot : pd.DataFrame
        Rating over time
    ticker : str
        Ticker associated with ratings
    """
    plt.figure(figsize=plot_autoscale(), dpi=PLOT_DPI)

    rot = df_rot.sort_values("period")
    plt.plot(pd.to_datetime(rot["period"]), rot["strongBuy"], c="green", lw=3)
    plt.plot(pd.to_datetime(rot["period"]), rot["buy"], c="lightgreen", lw=3)
    plt.plot(pd.to_datetime(rot["period"]), rot["hold"], c="grey", lw=3)
    plt.plot(pd.to_datetime(rot["period"]), rot["sell"], c="pink", lw=3)
    plt.plot(pd.to_datetime(rot["period"]), rot["strongSell"], c="red", lw=3)
    plt.xlim(
        pd.to_datetime(rot["period"].values[0]),
        pd.to_datetime(rot["period"].values[-1]),
    )
    plt.grid()
    plt.title(f"{ticker}'s ratings over time")
    plt.xlabel("Time")
    plt.ylabel("Rating")
    plt.legend(["Strong Buy", "Buy", "Hold", "Sell", "Strong Sell"])
    plt.gcf().autofmt_xdate()

    if gtff.USE_ION:
        plt.ion()

    plt.show()


@log_start_end(log=logger)
def rating_over_time(ticker: str, num: int, raw: bool, export: str):
    """Rating over time (monthly). [Source: Finnhub]

    Parameters
    ----------
    ticker : str
        Ticker to get ratings from
    num : int
        Number of last months ratings to show
    raw : bool
        Display raw data only
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    df_rot = finnhub_model.get_rating_over_time(ticker)

    if df_rot.empty:
        console.print("No ratings over time found", "\n")
        return

    if raw:
        d_cols = {
            "strongSell": "Strong Sell",
            "sell": "Sell",
            "hold": "Hold",
            "buy": "Buy",
            "strongBuy": "Strong Buy",
        }
        df_rot_raw = (
            df_rot[["period", "strongSell", "sell", "hold", "buy", "strongBuy"]]
            .rename(columns=d_cols)
            .head(num)
        )
        print_rich_table(
            df_rot_raw,
            headers=list(df_rot_raw.columns),
            show_index=False,
            title="Monthly Rating",
        )
    else:
        plot_rating_over_time(df_rot.head(num), ticker)

    console.print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "rot",
        df_rot,
    )
