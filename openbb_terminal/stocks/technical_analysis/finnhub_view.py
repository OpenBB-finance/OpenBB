"""Finnhub view"""
__docformat__ = "numpy"

import logging
import math
import os
from typing import List, Optional

from datetime import datetime
import mplfinance as mpf
import yfinance as yf
from matplotlib import pyplot as plt

from openbb_terminal.config_terminal import theme
from openbb_terminal.decorators import check_api_key
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data, plot_autoscale
from openbb_terminal.rich_config import console
from openbb_terminal.stocks.technical_analysis import finnhub_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
@check_api_key(["API_FINNHUB_KEY"])
def plot_pattern_recognition(
    ticker: str,
    resolution: str,
    export: str,
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Plot pattern recognition signal

    Parameters
    ----------
    ticker : str
        Ticker to display pattern recognition on top of the data
    resolution : str
        Resolution of data to get pattern recognition from
    export: str
        Format of export file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """

    pattern = finnhub_model.get_pattern_recognition(ticker, resolution)

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "pr",
        pattern,
    )

    l_segments = []
    for i in pattern:
        a_part = ("", "")
        if "aprice" in pattern[i]:
            if pattern[i]["aprice"] != 0 and not math.isnan(pattern[i]["aprice"]):
                a_part = (
                    datetime.utcfromtimestamp(pattern[i]["atime"]).strftime("%Y-%m-%d"),
                    pattern[i]["aprice"],
                )

        b_part = ("", "")
        if "bprice" in pattern[i]:
            if pattern[i]["bprice"] != 0 and not math.isnan(pattern[i]["bprice"]):
                b_part = (
                    datetime.utcfromtimestamp(pattern[i]["btime"]).strftime("%Y-%m-%d"),
                    pattern[i]["bprice"],
                )

        c_part = ("", "")
        if "cprice" in pattern[i]:
            if pattern[i]["cprice"] != 0 and not math.isnan(pattern[i]["cprice"]):
                c_part = (
                    datetime.utcfromtimestamp(pattern[i]["ctime"]).strftime("%Y-%m-%d"),
                    pattern[i]["cprice"],
                )

        d_part = ("", "")
        if "dprice" in pattern[i]:
            if pattern[i]["dprice"] != 0 and not math.isnan(pattern[i]["dprice"]):
                d_part = (
                    datetime.utcfromtimestamp(pattern[i]["dtime"]).strftime("%Y-%m-%d"),
                    pattern[i]["dprice"],
                )

        segment = (a_part, b_part, c_part, d_part)

        l_segment = list(segment)
        while ("", "") in l_segment:
            l_segment.remove(("", ""))
        segm = tuple(l_segment)

        l_segments.append(segm)

    start_time = 999999999999
    for i in pattern:
        if pattern[i]["atime"] < start_time:
            start_time = pattern[i]["atime"]

    df_stock = yf.download(
        ticker,
        start=datetime.utcfromtimestamp(start_time).strftime("%Y-%m-%d"),
        progress=False,
    )
    df_stock["date_id"] = (df_stock.index.date - df_stock.index.date.min()).astype(
        "timedelta64[D]"
    )
    df_stock["date_id"] = df_stock["date_id"].dt.days + 1

    df_stock["OC_High"] = df_stock[["Open", "Close"]].max(axis=1)
    df_stock["OC_Low"] = df_stock[["Open", "Close"]].min(axis=1)

    candle_chart_kwargs = {
        "type": "candle",
        "style": theme.mpf_style,
        "volume": False,
        "alines": l_segments,
        "xrotation": theme.xticks_rotation,
        "scale_padding": {"left": 0.3, "right": 1, "top": 0.8, "bottom": 0.8},
        "update_width_config": {
            "candle_linewidth": 0.6,
            "candle_width": 0.8,
            "volume_linewidth": 0.8,
            "volume_width": 0.8,
        },
        "warn_too_much_data": 10000,
    }
    # This plot has 2 axes
    if not external_axes:
        candle_chart_kwargs["returnfig"] = True
        candle_chart_kwargs["figratio"] = (10, 7)
        candle_chart_kwargs["figscale"] = 1.10
        candle_chart_kwargs["figsize"] = plot_autoscale()
        (fig, ax) = mpf.plot(df_stock, **candle_chart_kwargs)
        fig.suptitle(
            f"\n{ticker}",
            x=0.055,
            y=0.965,
            horizontalalignment="left",
        )

        theme.visualize_output(force_tight_layout=False)

    else:
        if len(external_axes) != 1:
            logger.error("Expected list of one axis item.")
            console.print("[red]Expected list of 1 axis items./n[/red]")
            return
        (ax,) = external_axes
        candle_chart_kwargs["ax"] = ax
        mpf.plot(df_stock, **candle_chart_kwargs)

    for ix in range(len(pattern.columns)):
        console.print(f"From {l_segments[ix][0][0]} to {l_segments[ix][-1][0]}")
        console.print(
            f"Pattern: {pattern[0]['patternname']} ({pattern[0]['patterntype']})", "\n"
        )
