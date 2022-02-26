"""bt view module"""
__docformat__ = "numpy"

import logging
import os
from datetime import datetime
from typing import List, Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yfinance as yf
from pandas.plotting import register_matplotlib_converters

from gamestonk_terminal.config_terminal import theme
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.helper_funcs import export_data, plot_autoscale
from gamestonk_terminal.rich_config import console
from gamestonk_terminal.stocks.backtesting import bt_model

logger = logging.getLogger(__name__)

register_matplotlib_converters()

np.seterr(divide="ignore")


@log_start_end(log=logger)
def display_whatif_scenario(
    ticker: str,
    num_shares_acquired: float,
    date_shares_acquired: datetime,
):
    """Display what if scenario

    Parameters
    ----------
    ticker: str
        Ticker to check what if scenario
    num_shares: float
        Number of shares acquired
    date_shares_acquired: str
        Date at which the shares were acquired
    """
    data = yf.download(ticker, progress=False)

    if not data.empty:
        data = data["Adj Close"]

    ipo_date = data.index[0]
    last_date = data.index[-1]

    if not date_shares_acquired:
        date_shares_acquired = ipo_date
        console.print("IPO date selected by default.")

    if date_shares_acquired > last_date:
        console.print("The date selected is in the future. Select a valid date.", "\n")
        return

    if date_shares_acquired < ipo_date:
        console.print(
            f"{ticker} had not IPO at that date. Thus, changing the date to IPO on the {ipo_date.strftime('%Y-%m-%d')}",
            "\n",
        )
        date_shares_acquired = ipo_date

    initial_shares_value = (
        data[data.index > date_shares_acquired].values[0] * num_shares_acquired
    )

    if (num_shares_acquired - int(num_shares_acquired)) > 0:
        nshares = round(num_shares_acquired, 2)
    else:
        nshares = round(num_shares_acquired)

    shares = "share"
    these = "This"
    if nshares > 1:
        shares += "s"
        these = "These"

    console.print(
        f"If you had acquired {nshares} {shares} of {ticker} on "
        f"{date_shares_acquired.strftime('%Y-%m-%d')} with a cost of {initial_shares_value:.2f}."
    )

    current_shares_value = (
        data[data.index > date_shares_acquired].values[-1] * num_shares_acquired
    )
    if current_shares_value > initial_shares_value:
        pct = 100 * (
            (current_shares_value - initial_shares_value) / initial_shares_value
        )
        console.print(
            f"{these} would be worth {current_shares_value:.2f}. Which represents an increase of {pct:.2f}%.",
            "\n",
        )
    else:
        pct = 100 * (
            (initial_shares_value - current_shares_value) / initial_shares_value
        )
        console.print(
            f"{these} would be worth {current_shares_value:.2f}. Which represents an decrease of {pct:.2f}%.",
            "\n",
        )


@log_start_end(log=logger)
def display_simple_ema(
    ticker: str,
    df_stock: pd.DataFrame,
    ema_length: int,
    spy_bt: bool = True,
    no_bench: bool = False,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Strategy where stock is bought when Price > EMA(l)

    Parameters
    ----------
    ticker : str
        Stock ticker
    df_stock : pd.Dataframe
        Dataframe of prices
    ema_length : int
        Length of ema window
    spy_bt : bool
        Boolean to add spy comparison
    no_bench : bool
        Boolean to not show buy and hold comparison
    export : bool
        Format to export backtest results
    external_axes : Optional[List[plt.Axes]], optional
        External axes (3 axes are expected in the list), by default None
    """

    # This plot has 1 axis
    if not external_axes:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    else:
        if len(external_axes) != 1:
            logger.error("Expected list of one axis item.")
            console.print("[red]Expected list of one axis item./n[/red]")
            return
        (ax,) = external_axes

    res = bt_model.ema_strategy(ticker, df_stock, ema_length, spy_bt, no_bench)
    res.plot(title=f"Equity for EMA({ema_length})", ax=ax)

    theme.style_primary_axis(ax)

    if not external_axes:
        theme.visualize_output()

    console.print(res.display(), "\n")

    export_data(
        export, os.path.dirname(os.path.abspath(__file__)), "simple_ema", res.stats
    )


@log_start_end(log=logger)
def display_ema_cross(
    ticker: str,
    df_stock: pd.DataFrame,
    short_ema: int,
    long_ema: int,
    spy_bt: bool = True,
    no_bench: bool = False,
    shortable: bool = True,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):  # pylint: disable=R0913
    """Strategy where we go long/short when EMA(short) is greater than/less than EMA(short)

    Parameters
    ----------
    ticker : str
        Stock ticker
    df_stock : pd.Dataframe
        Dataframe of prices
    short_ema : int
        Length of short ema window
    long_ema : int
        Length of long ema window
    spy_bt : bool
        Boolean to add spy comparison
    no_bench : bool
        Boolean to not show buy and hold comparison
    shortable : bool
        Boolean to allow for selling of the stock at cross
    export : str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (3 axes are expected in the list), by default None
    """
    # This plot has 1 axis
    if not external_axes:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    else:
        if len(external_axes) != 1:
            logger.error("Expected list of one axis item.")
            console.print("[red]Expected list of one axis item./n[/red]")
            return
        (ax,) = external_axes

    res = bt_model.ema_cross_strategy(
        ticker, df_stock, short_ema, long_ema, spy_bt, no_bench, shortable
    )
    res.plot(title=f"EMA Cross for EMA({short_ema})/EMA({long_ema})", ax=ax)

    theme.style_primary_axis(ax)

    if not external_axes:
        theme.visualize_output()

    export_data(
        export, os.path.dirname(os.path.abspath(__file__)), "ema_cross", res.stats
    )


# pylint:disable=too-many-arguments
@log_start_end(log=logger)
def display_rsi_strategy(
    ticker: str,
    df_stock: pd.DataFrame,
    periods: int,
    low_rsi: int,
    high_rsi: int,
    spy_bt: bool = True,
    no_bench: bool = False,
    shortable: bool = True,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Strategy that buys when the stock is less than a threshold and shorts when it exceeds a threshold.

    Parameters
    ----------
    ticker : str
        Stock ticker
    df_stock : pd.Dataframe
        Dataframe of prices
    periods : int
        Number of periods for RSI calculation
    low_rsi : int
        Low RSI value to buy
    high_rsi : int
        High RSI value to sell
    spy_bt : bool
        Boolean to add spy comparison
    no_bench : bool
        Boolean to not show buy and hold comparison
    shortable : bool
        Boolean to allow for selling of the stock at cross
    export : str
        Format to export backtest results
    external_axes : Optional[List[plt.Axes]], optional
        External axes (3 axes are expected in the list), by default None
    """
    # This plot has 1 axis
    if not external_axes:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    else:
        if len(external_axes) != 1:
            logger.error("Expected list of one axis item.")
            console.print("[red]Expected list of one axis item./n[/red]")
            return
        (ax,) = external_axes

    res = bt_model.rsi_strategy(
        ticker, df_stock, periods, low_rsi, high_rsi, spy_bt, no_bench, shortable
    )

    res.plot(title=f"RSI Strategy between ({low_rsi}, {high_rsi})", ax=ax)

    theme.style_primary_axis(ax)

    if not external_axes:
        theme.visualize_output()

    export_data(
        export, os.path.dirname(os.path.abspath(__file__)), "rsi_corss", res.stats
    )
