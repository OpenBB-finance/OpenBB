# IMPORTATION STANDARD
import logging
import os

# IMPORTATION THIRDPARTY
from typing import List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# IMPORTATION INTERNAL
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table
from openbb_terminal.plots_core.plotly_helper import OpenBBFigure
from openbb_terminal.rich_config import console
from openbb_terminal.stocks.options.op_helpers import calculate_max_pain

logger = logging.getLogger(__name__)

# pylint: disable=C0302,R0913


def get_strikes(
    min_sp: float, max_sp: float, current_price: float
) -> Tuple[float, float]:
    if min_sp == -1:
        min_strike = 0.75 * current_price
    else:
        min_strike = min_sp

    if max_sp == -1:
        max_strike = 1.25 * current_price
    else:
        max_strike = max_sp

    return min_strike, max_strike


def get_max_pain(calls: pd.DataFrame, puts: pd.DataFrame) -> float:
    call_oi = calls.set_index("strike")["openInterest"] / 1000
    put_oi = puts.set_index("strike")["openInterest"] / 1000
    df_opt = pd.merge(call_oi, put_oi, left_index=True, right_index=True)
    df_opt = df_opt.rename(
        columns={"openInterest_x": "OI_call", "openInterest_y": "OI_put"}
    )
    return calculate_max_pain(df_opt)


def print_raw(
    calls: pd.DataFrame,
    puts: pd.DataFrame,
    title: str,
    calls_only: bool = False,
    puts_only: bool = False,
):
    if not puts_only:
        print_rich_table(
            calls,
            headers=list(calls.columns),
            show_index=False,
            title=f"{title} - Calls",
        )
    if not calls_only:
        print_rich_table(
            puts,
            headers=list(puts.columns),
            show_index=False,
            title=f"{title} - Puts",
        )


@log_start_end(log=logger)
def plot_vol(
    chain: pd.DataFrame,
    current_price: float,
    symbol: str,
    expiry: str,
    min_sp: float = -1,
    max_sp: float = -1,
    calls_only: bool = False,
    puts_only: bool = False,
    raw: bool = False,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Plot volume

    Parameters
    ----------
    chain: pd.Dataframe
        Dataframe with options chain
    current_price: float
        Current price of selected symbol
    symbol: str
        Ticker symbol
    expiry: str
        expiration date for options
    min_sp: float
        Min strike to consider
    max_sp: float
        Max strike to consider
    calls_only: bool
        Show calls only
    puts_only: bool
        Show puts only
    export: str
        Format to export file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None


    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> aapl_chain_data = openbb.stocks.options.chains("AAPL", expiration="2023-07-21", source="Nasdaq")
    >>> aapl_price = openbb.stocks.options.price("AAPL", source="Nasdaq")
    >>> openbb.stocks.options.vol(
            chain=aapl_chain_data,
            symbol="AAPL",
            current_price=aapl_price,
            expiry="2023-07-21",
        )
    """
    calls = chain[chain["optionType"] == "call"]
    puts = chain[chain["optionType"] == "put"]

    min_strike, max_strike = get_strikes(min_sp, max_sp, current_price)
    title = f"Volume for {symbol.upper()} expiring {expiry}"

    if raw:
        print_raw(calls, puts, title, calls_only, puts_only)

    fig = OpenBBFigure(
        title=title,
        xaxis_title="Strike Price",
        yaxis_title="Volume [1k]",
        xaxis_range=[min_strike, max_strike],
    )

    if not puts_only:
        call_v = calls.set_index("strike")["volume"] / 1000
        fig.add_scatter(
            x=call_v.index, y=call_v.values, mode="lines+markers", name="Calls"
        )
    if not calls_only:
        put_v = puts.set_index("strike")["volume"] / 1000
        fig.add_scatter(
            x=put_v.index, y=put_v.values, mode="lines+markers", name="Puts"
        )

    fig.add_vline(x=current_price, line_dash="dash", line_width=2, name="Current Price")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        f"vol_{symbol}_{expiry}",
        chain,
    )
    return fig.show() if not external_axes else fig


@log_start_end(log=logger)
def plot_oi(
    chain: pd.DataFrame,
    current_price: float,
    symbol: str,
    expiry: str,
    min_sp: float = -1,
    max_sp: float = -1,
    calls_only: bool = False,
    puts_only: bool = False,
    raw: bool = False,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Plot open interest

    Parameters
    ----------
    chain: pd.Dataframe
        Dataframe with options chain
    current_price: float
        Current price of selected symbol
    symbol: str
        Ticker symbol
    expiry: str
        expiration date for options
    min_sp: float
        Min strike to consider
    max_sp: float
        Max strike to consider
    calls_only: bool
        Show calls only
    puts_only: bool
        Show puts only
    export: str
        Format to export file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> aapl_chain_data = openbb.stocks.options.chains("AAPL", expiration="2023-07-21", source="Nasdaq")
    >>> aapl_price = openbb.stocks.options.price("AAPL", source="Nasdaq")
    >>> openbb.stocks.options.oi(
            chain=aapl_chain_data,
            symbol="AAPL",
            current_price=aapl_price,
            expiry="2023-07-21",
        )
    """
    calls = chain[chain["optionType"] == "call"]
    puts = chain[chain["optionType"] == "put"]

    min_strike, max_strike = get_strikes(min_sp, max_sp, current_price)
    max_pain = get_max_pain(calls, puts)
    title = f"Open Interest for {symbol.upper()} expiring {expiry}"

    if raw:
        print_raw(calls, puts, title, calls_only, puts_only)

    fig = OpenBBFigure(
        title=title,
        xaxis_title="Strike Price",
        yaxis_title="Open Interest (1k) ",
        xaxis_range=[min_strike, max_strike],
    )
    if not puts_only:
        call_oi = calls.set_index("strike")["openInterest"] / 1000
        fig.add_scatter(
            x=call_oi.index, y=call_oi.values, mode="lines+markers", name="Calls"
        )
    if not calls_only:
        put_oi = puts.set_index("strike")["openInterest"] / 1000
        fig.add_scatter(
            x=put_oi.index, y=put_oi.values, mode="lines+markers", name="Puts"
        )

    fig.add_vline_legend(
        x=current_price,
        name="Current Price",
        line=dict(dash="dash", width=2, color="grey"),
    )
    fig.add_vline_legend(
        x=max_pain,
        name=f"Max Pain: {max_pain}",
        line=dict(dash="dash", width=2, color="white"),
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        f"oi_{symbol}_{expiry}",
        chain,
    )

    return fig.show() if not external_axes else fig


@log_start_end(log=logger)
def plot_voi(
    chain: pd.DataFrame,
    current_price: float,
    symbol: str,
    expiry: str,
    min_sp: float = -1,
    max_sp: float = -1,
    raw: bool = False,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Plot volume and open interest

    Parameters
    ----------
    chain: pd.Dataframe
        Dataframe with options chain
    current_price: float
        Current price of selected symbol
    symbol: str
        Stock ticker symbol
    expiry: str
        Option expiration
    min_sp: float
        Min strike price
    max_sp: float
        Max strike price
    export: str
        Format for exporting data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> aapl_chain_data = openbb.stocks.options.chains("AAPL", expiration="2023-07-21", source="Nasdaq")
    >>> aapl_price = openbb.stocks.options.price("AAPL", source="Nasdaq")
    >>> openbb.stocks.options.voi(
            chain=aapl_chain_data,
            symbol="AAPL",
            current_price=aapl_price,
            expiry="2023-07-21",
        )
    """
    calls = chain[chain["optionType"] == "call"]
    puts = chain[chain["optionType"] == "put"]

    min_strike, max_strike = get_strikes(min_sp, max_sp, current_price)
    max_pain = get_max_pain(calls, puts)
    title = f"Volume and Open Interest for {symbol.upper()} expiring {expiry}"

    # Process Data
    def get_df_options(df: pd.DataFrame, opt_type: str):
        df = df.pivot_table(
            index="strike", values=["volume", "openInterest"], aggfunc="sum"
        ).reindex()
        df["strike"] = df.index
        df["type"] = opt_type
        df["openInterest"] = df["openInterest"] * (-1 if opt_type == "puts" else 1)
        df["volume"] = df["volume"] * (-1 if opt_type == "puts" else 1)
        df["oi+v"] = df["openInterest"] + df["volume"]
        df["spot"] = round(current_price, 2)

        # we use the percentile 50 to get 50% of upper volume data
        volume_percentile_threshold = 50
        vol = np.percentile(df["oi+v"], volume_percentile_threshold)

        df = df[
            (df["strike"] >= min_strike)
            & (df["strike"] <= max_strike)
            & (df["oi+v"] >= vol if opt_type == "calls" else df["oi+v"] <= vol)
        ]

        return df

    df_calls = get_df_options(calls, "calls")
    df_puts = get_df_options(puts, "puts")

    df_calls = df_calls.loc[df_calls.index.intersection(df_puts.index)]
    df_puts = df_puts.loc[df_puts.index.intersection(df_calls.index)]

    if df_calls.empty and df_puts.empty:
        return console.print(
            "The filtering applied is too strong, there is no data available for such conditions.\n"
        )

    fig = OpenBBFigure(
        title=title,
        xaxis_title="Volume",
        yaxis_title="Strike Price",
    )

    fig.add_bar(
        x=df_calls["oi+v"],
        y=df_calls["strike"],
        name="Calls: Open Interest",
        orientation="h",
        marker_color="lightgreen",
    )
    fig.add_bar(
        x=df_calls["volume"],
        y=df_calls["strike"],
        name="Calls: Volume",
        orientation="h",
        marker_color="green",
    )
    fig.add_bar(
        x=df_puts["oi+v"],
        y=df_puts["strike"],
        name="Puts: Open Interest",
        orientation="h",
        marker_color="pink",
    )
    fig.add_bar(
        x=df_puts["volume"],
        y=df_puts["strike"],
        name="Puts: Volume",
        orientation="h",
        marker_color="red",
    )
    fig.add_hline_legend(
        y=current_price,
        name="Current stock price",
        line=dict(dash="dash", width=2, color="white"),
    )
    fig.add_hline_legend(
        y=max_pain,
        name=f"Max pain = {max_pain}",
        line=dict(dash="dash", width=2, color="red"),
    )

    fig.update_layout(barmode="relative", hovermode="y unified")

    if raw:
        print_raw(calls, puts, title)

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        f"voi_{symbol}_{expiry}",
        chain,
    )

    return fig.show() if not external_axes else fig


@log_start_end(log=logger)
def display_expiry_dates(expiry_dates: list):
    """Display expiry dates

    Parameters
    ----------
    expiry_dates: list
        The expiry dates of the chosen ticker.
    """
    expiry_dates_df = pd.DataFrame(expiry_dates, columns=["Date"])

    print_rich_table(
        expiry_dates_df,
        headers=list(expiry_dates_df.columns),
        title="Available expiry dates",
        show_index=True,
        index_name="Identifier",
    )
