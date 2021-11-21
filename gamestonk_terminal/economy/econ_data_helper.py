"""Econ Data Helper Module"""
__docformat__ = "numpy"

import os
import pathlib
from datetime import datetime, timedelta
import pandas as pd
import mplfinance as mpf

from gamestonk_terminal.stocks import stocks_helper


# pylint: disable=too-many-arguments
def draw_graph(
    ticker: str,
    report_cache_dir: str,
    time_delta: int = 180,
    line_type: str = "candle",
    draw_mas: tuple = (20, 50),
    draw_volume: bool = True,
    high_trend: bool = True,
    low_trend: bool = True,
):
    """Draw Graph is a helper that wraps mplfinance, caching and trendline
    Parameters
    ----------
    ticker : str
        Stock ticker to draw
    report_cache_dir : str
        Ticker data cache directory to use
    time_delta : int, optional
        Graph period in days, by default 180
    line_type : str, optional
        Graph line type to pass to mplfinance, by default "candle"
    draw_mas : tuple, optional
        SMAs to draw, by default (20, 50)
    draw_volume : bool, optional
        Switch to draw trading volume by default True
    high_trend : bool, optional
        Switch to draw high trend line, by default True
    low_trend : bool, optional
        Switch to draw low trend line, by default True
    """
    if report_cache_dir:
        df_stock_cache = pathlib.Path(
            report_cache_dir, f"{ticker}_stock_data_{time_delta}.pkl"
        )
        if os.path.isfile(df_stock_cache):
            df_stock = pd.read_pickle(df_stock_cache)
        else:
            df_stock = stocks_helper.load_ticker(
                ticker,
                (datetime.now() - timedelta(days=time_delta)).strftime("%Y-%m-%d"),
            )
            df_stock = stocks_helper.find_trendline(df_stock, "OC_High", "high")
            df_stock = stocks_helper.find_trendline(df_stock, "OC_Low", "how")
            df_stock.to_pickle(df_stock_cache)

    else:
        df_stock = stocks_helper.load_ticker(
            ticker, (datetime.now() - timedelta(days=time_delta)).strftime("%Y-%m-%d")
        )
        df_stock = stocks_helper.find_trendline(df_stock, "OC_High", "high")
        df_stock = stocks_helper.find_trendline(df_stock, "OC_Low", "how")

    mc = mpf.make_marketcolors(
        up="green", down="red", edge="black", wick="black", volume="in", ohlc="i"
    )
    s = mpf.make_mpf_style(marketcolors=mc, gridstyle=":", y_on_right=True)

    ap0 = []

    if "OC_High_trend" in df_stock.columns and high_trend:
        ap0.append(
            mpf.make_addplot(df_stock["OC_High_trend"], color="g"),
        )

    if "OC_Low_trend" in df_stock.columns and low_trend:
        ap0.append(
            mpf.make_addplot(df_stock["OC_Low_trend"], color="b"),
        )

    mpf.plot(
        df_stock,
        type=line_type,
        mav=draw_mas,
        volume=draw_volume,
        addplot=ap0,
        xrotation=0,
        style=s,
        figratio=(10, 7),
        figscale=2.00,
        update_width_config=dict(
            candle_linewidth=1.0, candle_width=0.8, volume_linewidth=1.0
        ),
    )
