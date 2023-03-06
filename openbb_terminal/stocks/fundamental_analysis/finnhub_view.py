""" Finnhub View """
__docformat__ = "numpy"

import logging
import os
from typing import List, Optional

import pandas as pd
from matplotlib import pyplot as plt
from pandas.plotting import register_matplotlib_converters

from openbb_terminal.config_plot import PLOT_DPI
from openbb_terminal.config_terminal import theme
from openbb_terminal.decorators import check_api_key, log_start_end
from openbb_terminal.helper_funcs import (
    export_data,
    is_valid_axes_count,
    plot_autoscale,
    print_rich_table,
)
from openbb_terminal.stocks.fundamental_analysis import finnhub_model

logger = logging.getLogger(__name__)

register_matplotlib_converters()


@log_start_end(log=logger)
def plot_rating_over_time(
    data: pd.DataFrame,
    symbol: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Plot rating over time

    Parameters
    ----------
    data: pd.DataFrame
        Rating over time
    symbol: str
        Ticker symbol associated with ratings
    external_axes: Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """
    # This plot has 1 axis
    if not external_axes:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    elif is_valid_axes_count(external_axes, 1):
        (ax,) = external_axes
    else:
        return

    rot = data.sort_values("period")
    ax.plot(pd.to_datetime(rot["period"]), rot["strongBuy"], c="green", lw=3)
    ax.plot(pd.to_datetime(rot["period"]), rot["buy"], c="lightgreen", lw=3)
    ax.plot(pd.to_datetime(rot["period"]), rot["hold"], c="grey", lw=3)
    ax.plot(pd.to_datetime(rot["period"]), rot["sell"], c="pink", lw=3)
    ax.plot(pd.to_datetime(rot["period"]), rot["strongSell"], c="red", lw=3)
    ax.set_xlim(
        pd.to_datetime(rot["period"].values[0]),
        pd.to_datetime(rot["period"].values[-1]),
    )
    ax.set_title(f"{symbol}'s ratings over time")
    ax.set_ylabel("Rating")
    ax.legend(["Strong Buy", "Buy", "Hold", "Sell", "Strong Sell"])

    theme.style_primary_axis(ax)

    if not external_axes:
        theme.visualize_output()


@log_start_end(log=logger)
@check_api_key(["API_FINNHUB_KEY"])
def rating_over_time(
    symbol: str,
    limit: int = 10,
    raw: bool = False,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Rating over time (monthly). [Source: Finnhub]

    Parameters
    ----------
    ticker : str
        Ticker to get ratings from
    limit : int
        Number of last months ratings to show
    raw: bool
        Display raw data only
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]]
        External axes (1 axis is expected in the list), by default None
    """
    df_rot = finnhub_model.get_rating_over_time(symbol)

    if df_rot.empty:
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
            .head(limit)
        )
        print_rich_table(
            df_rot_raw,
            headers=list(df_rot_raw.columns),
            show_index=False,
            title="Monthly Rating",
        )
    else:
        plot_rating_over_time(df_rot.head(limit), symbol, external_axes)

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "rot",
        df_rot,
        sheet_name,
    )
