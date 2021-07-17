import argparse
from typing import List
import math
from datetime import datetime
import requests
import yfinance as yf
import mplfinance as mpf
import pandas as pd
from gamestonk_terminal import config_terminal as cfg
from gamestonk_terminal.helper_funcs import (
    parse_known_args_and_warn,
    plot_autoscale,
)


def get_pattern_recognition(ticker: str, resolution: str) -> pd.DataFrame:
    """Get pattern recognition data

    Parameters
    ----------
    ticker : str
        Ticker to get pattern recognition data
    resolution : str
        Resolution of data to get pattern recognition from

    Returns
    -------
    pd.DataFrame
        Get datapoints corresponding to pattern signal data
    """
    response = requests.get(
        f"https://finnhub.io/api/v1/scan/pattern?symbol={ticker}&resolution={resolution}&token={cfg.API_FINNHUB_KEY}"
    )
    if response.status_code == 200:
        d_data = response.json()
        if "points" in d_data:
            return pd.DataFrame(d_data["points"]).T

    return pd.DataFrame()


def plot_pattern_recognition(ticker: str, pattern: pd.DataFrame):
    """Plot pattern recognition signal

    Parameters
    ----------
    ticker : str
        Ticker to display pattern recognition on top of the data
    pattern : pd.DataFrame
        Pattern recognition signal data
    """
    l_segments = list()
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
        print(f"From {l_segments[ix][0][0]} to {l_segments[ix][-1][0]}")
        print(
            f"Pattern: {pattern[0]['patternname']} ({pattern[0]['patterntype']})", "\n"
        )


def pattern_recognition_view(other_args: List[str], ticker: str):
    """Display pattern recognition signals on the data

    Parameters
    ----------
    other_args : List[str]
        Command line arguments to be processed with argparse
    ticker : str
        Ticker to display pattern recognition on top of the data
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="pr",
        description="""
            Display pattern recognition signals on the data. [Source: https://finnhub.io]
        """,
    )
    parser.add_argument(
        "-r",
        "--resolution",
        action="store",
        dest="resolution",
        type=str,
        default="D",
        choices=["1", "5", "15", "30", "60", "D", "W", "M"],
        help="Plot resolution to look for pattern signals",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        df_pattern = get_pattern_recognition(ticker, ns_parser.resolution)

        if df_pattern.empty:
            print("No pattern identified in this data", "\n")
            return

        plot_pattern_recognition(ticker, df_pattern)

    except Exception as e:
        print(e, "\n")
