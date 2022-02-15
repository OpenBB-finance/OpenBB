""" Finnhub View """
__docformat__ = "numpy"

import logging
import os
from typing import List, Optional

import pandas as pd
from matplotlib import pyplot as plt
from pandas.plotting import register_matplotlib_converters

from gamestonk_terminal.config_terminal import theme
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
def plot_rating_over_time(
    df_rot: pd.DataFrame,
    ticker: str,
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Plot rating over time

    Parameters
    ----------
    df_rot : pd.DataFrame
        Rating over time
    ticker : str
        Ticker associated with ratings
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    external_axes: Optional[List[plt.Axes]] = None,

    """
    # This plot has 1 axis
    if not external_axes:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    else:
        if len(external_axes) != 1:
            console.print("[red]Expected list of one axis item./n[/red]")
            return
        (ax,) = external_axes

    rot = df_rot.sort_values("period")
    ax.plot(pd.to_datetime(rot["period"]), rot["strongBuy"], c="green", lw=3)
    ax.plot(pd.to_datetime(rot["period"]), rot["buy"], c="lightgreen", lw=3)
    ax.plot(pd.to_datetime(rot["period"]), rot["hold"], c="grey", lw=3)
    ax.plot(pd.to_datetime(rot["period"]), rot["sell"], c="pink", lw=3)
    ax.plot(pd.to_datetime(rot["period"]), rot["strongSell"], c="red", lw=3)
    ax.set_xlim(
        pd.to_datetime(rot["period"].values[0]),
        pd.to_datetime(rot["period"].values[-1]),
    )
    ax.set_title(f"{ticker}'s ratings over time")
    ax.set_ylabel("Rating")
    ax.legend(["Strong Buy", "Buy", "Hold", "Sell", "Strong Sell"])

    theme.style_primary_axis(ax)

    if not external_axes:
        theme.visualize_output()


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
