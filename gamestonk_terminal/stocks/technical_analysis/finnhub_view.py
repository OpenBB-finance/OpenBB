"""Finnhub view"""
__docformat__ = "numpy"

import os

import math
from datetime import datetime
import yfinance as yf
import mplfinance as mpf

from gamestonk_terminal.helper_funcs import plot_autoscale, export_data
from gamestonk_terminal.stocks.technical_analysis import finnhub_model
from gamestonk_terminal.rich_config import console


def plot_pattern_recognition(ticker: str, resolution: str, export: str):
    """Plot pattern recognition signal

    Parameters
    ----------
    ticker : str
        Ticker to display pattern recognition on top of the data
    resolution : str
        Resolution of data to get pattern recognition from
    export: str
        Format of export file
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

    mc = mpf.make_marketcolors(
        up="green", down="red", edge="black", wick="black", volume="in", ohlc="i"
    )

    s = mpf.make_mpf_style(marketcolors=mc, gridstyle=":", y_on_right=False)

    mpf.plot(
        df_stock,
        type="candle",
        volume=False,
        title=f"\n{ticker}",
        alines=l_segments,
        xrotation=10,
        style=s,
        figratio=(10, 7),
        figscale=1.10,
        figsize=plot_autoscale(),
        update_width_config=dict(
            candle_linewidth=1.0, candle_width=0.8, volume_linewidth=1.0
        ),
    )

    for ix in range(len(pattern.columns)):
        console.print(f"From {l_segments[ix][0][0]} to {l_segments[ix][-1][0]}")
        console.print(
            f"Pattern: {pattern[0]['patternname']} ({pattern[0]['patterntype']})", "\n"
        )
