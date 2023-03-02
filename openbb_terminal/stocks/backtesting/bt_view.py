"""bt view module"""
__docformat__ = "numpy"

import logging
import os
from datetime import datetime
from typing import Optional

import numpy as np
import pandas as pd
import yfinance as yf

from openbb_terminal import OpenBBFigure
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data, is_intraday
from openbb_terminal.rich_config import console
from openbb_terminal.stocks.backtesting import bt_model

logger = logging.getLogger(__name__)


np.seterr(divide="ignore")


@log_start_end(log=logger)
def display_whatif_scenario(
    symbol: str,
    date_shares_acquired: Optional[datetime] = None,
    num_shares_acquired: float = 1,
):
    """Display what if scenario

    Parameters
    ----------
    symbol: str
        Ticker to check what if scenario
    date_shares_acquired: str
        Date at which the shares were acquired
    num_shares_acquired: float
        Number of shares acquired
    """
    data = yf.download(symbol, progress=False, ignore_tz=True)

    if not data.empty:
        data = data["Adj Close"]

    ipo_date = data.index[0]
    last_date = data.index[-1]

    if not date_shares_acquired:
        date_shares_ac = ipo_date
        console.print("IPO date selected by default.")
    else:
        date_shares_ac = date_shares_acquired

    if date_shares_ac > last_date:
        console.print("The date selected is in the future. Select a valid date.", "\n")
        return

    if date_shares_ac < ipo_date:
        console.print(
            f"{symbol} had not IPO at that date. Thus, changing the date to IPO on the {ipo_date.strftime('%Y-%m-%d')}",
            "\n",
        )
        date_shares_ac = ipo_date

    initial_shares_value = (
        data[data.index > date_shares_ac].values[0] * num_shares_acquired
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
        f"If you had acquired {nshares} {shares} of {symbol} on "
        f"{date_shares_ac.strftime('%Y-%m-%d')} with a cost of {initial_shares_value:.2f}."
    )

    current_shares_value = (
        data[data.index > date_shares_ac].values[-1] * num_shares_acquired
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
    symbol: str,
    data: pd.DataFrame,
    ema_length: int = 20,
    spy_bt: bool = True,
    no_bench: bool = False,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
):
    """Strategy where stock is bought when Price > EMA(l)

    Parameters
    ----------
    symbol : str
        Stock ticker
    data : pd.Dataframe
        Dataframe of prices
    ema_length : int
        Length of ema window
    spy_bt : bool
        Boolean to add spy comparison
    no_bench : bool
        Boolean to not show buy and hold comparison
    export : bool
        Format to export backtest results
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    # TODO: Help Wanted!
    # Implement support for backtesting on intraday data
    if is_intraday(data):
        console.print("Backtesting on intraday data is not yet supported.")
        console.print("Submit a feature request to let us know that you need it here:")
        return console.print("https://openbb.co/request-a-feature")

    fig = OpenBBFigure(xaxis_title="Date").set_title(f"Equity for EMA({ema_length})")

    res = bt_model.ema_strategy(symbol, data, ema_length, spy_bt, no_bench)
    df_res = res._get_series(None).rebase()  # pylint: disable=protected-access

    for col in df_res.columns:
        fig.add_scatter(
            x=df_res.index,
            y=df_res[col],
            mode="lines",
            name=col,
        )

    console.print(res.display(), "\n")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "simple_ema",
        res.stats,
        sheet_name,
        fig,
    )

    return fig.show(external=external_axes)


@log_start_end(log=logger)
def display_emacross(
    symbol: str,
    data: pd.DataFrame,
    short_ema: int = 20,
    long_ema: int = 50,
    spy_bt: bool = True,
    no_bench: bool = False,
    shortable: bool = True,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
):  # pylint: disable=R0913
    """Strategy where we go long/short when EMA(short) is greater than/less than EMA(short)

    Parameters
    ----------
    symbol : str
        Stock ticker
    data : pd.Dataframe
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
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    # TODO: Help Wanted!
    # Implement support for backtesting on intraday data
    if is_intraday(data):
        console.print("Backtesting on intraday data is not yet supported.")
        console.print("Submit a feature request to let us know that you need it here:")
        return console.print("https://openbb.co/request-a-feature")

    fig = OpenBBFigure(xaxis_title="Date").set_title(
        f"Equity for EMA({short_ema})/EMA({long_ema})"
    )

    res = bt_model.emacross_strategy(
        symbol, data, short_ema, long_ema, spy_bt, no_bench, shortable
    )
    df_res = res._get_series(None).rebase()  # pylint: disable=protected-access

    for col in df_res.columns:
        fig.add_scatter(
            x=df_res.index,
            y=df_res[col],
            mode="lines",
            name=col,
        )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "emacross",
        res.stats,
        sheet_name,
        fig,
    )
    return fig.show(external=external_axes)


# pylint:disable=too-many-arguments
@log_start_end(log=logger)
def display_rsi_strategy(
    symbol: str,
    data: pd.DataFrame,
    periods: int = 14,
    low_rsi: int = 30,
    high_rsi: int = 70,
    spy_bt: bool = True,
    no_bench: bool = False,
    shortable: bool = True,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
):
    """Strategy that buys when the stock is less than a threshold and shorts when it exceeds a threshold.

    Parameters
    ----------
    symbol : str
        Stock ticker
    data : pd.Dataframe
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
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    # TODO: Help Wanted!
    # Implement support for backtesting on intraday data
    if is_intraday(data):
        console.print("Backtesting on intraday data is not yet supported.")
        console.print("Submit a feature request to let us know that you need it here:")
        return console.print("https://openbb.co/request-a-feature")

    fig = OpenBBFigure(xaxis_title="Date").set_title(
        f"Equity for RSI({periods}) between ({low_rsi}, {high_rsi})"
    )

    res = bt_model.rsi_strategy(
        symbol, data, periods, low_rsi, high_rsi, spy_bt, no_bench, shortable
    )
    df_res = res._get_series(None).rebase()  # pylint: disable=protected-access

    for col in df_res.columns:
        fig.add_scatter(
            x=df_res.index,
            y=df_res[col],
            mode="lines",
            name=col,
        )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "rsi_corss",
        res.stats,
        sheet_name,
        fig,
    )
    return fig.show(external=external_axes)
