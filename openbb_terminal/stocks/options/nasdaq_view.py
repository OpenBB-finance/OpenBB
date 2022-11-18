"""Nasdaq View"""
__docformat__ = "numpy"

import logging
import os
from typing import List, Optional

import matplotlib.pyplot as plt

import openbb_terminal.config_plot as cfp
from openbb_terminal.config_terminal import theme
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    export_data,
    is_valid_axes_count,
    plot_autoscale,
    print_rich_table,
)
from openbb_terminal.stocks.options import nasdaq_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_oi(
    symbol: str,
    expiry: str,
    min_sp: float = -1,
    max_sp: float = -1,
    raw: bool = False,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Plot open interest

    Parameters
    ----------
    symbol: str
        Ticker symbol
    expiry: str
        Expiry date for options
    min_sp: float
        Min strike to consider
    max_sp: float
        Max strike to consider
    raw: bool
        Flag to display raw data
    export: str
        Format to export file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """
    option_chain = nasdaq_model.get_chain_given_expiration(symbol, expiry)
    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "oi_nasdaq",
        option_chain,
    )
    current_price = nasdaq_model.get_last_price(symbol)

    if min_sp == -1:
        min_strike = 0.75 * current_price
    else:
        min_strike = min_sp

    if max_sp == -1:
        max_strike = 1.25 * current_price
    else:
        max_strike = max_sp

    if external_axes is None:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=cfp.PLOT_DPI)
    elif is_valid_axes_count(external_axes, 1):
        (ax,) = external_axes
    else:
        return
    ax.plot(
        option_chain.strike,
        option_chain["c_Openinterest"] / 1000,
        ls="-",
        marker="o",
        label="Calls",
    )
    ax.plot(
        option_chain.strike,
        option_chain["p_Openinterest"] / 1000,
        ls="-",
        marker="o",
        label="Puts",
    )

    ax.axvline(current_price, lw=2, ls="--", label="Current Price", alpha=0.7)
    ax.set_xlabel("Strike Price")
    ax.set_ylabel("Open Interest (1k) ")
    ax.set_xlim(min_strike, max_strike)
    ax.legend(loc="best", fontsite="x-small")
    ax.set_title(f"Open Interest for {symbol.upper()} expiring {expiry}")

    theme.style_primary_axis(ax)
    if external_axes is None:
        theme.visualize_output()

    if raw:
        to_print = option_chain[["c_Openinterest", "strike", "p_Openinterest"]]

        print_rich_table(
            to_print[(to_print.strike < max_strike) & (to_print.strike > min_strike)],
            headers=to_print.columns,
            title=f"Open Interest for {symbol} expiring on {expiry}.",
        )


@log_start_end(log=logger)
def display_volume(
    symbol: str,
    expiry: str,
    min_sp: float = -1,
    max_sp: float = -1,
    raw: bool = False,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Plot volume

    Parameters
    ----------
    symbol: str
        Ticker symbol
    expiry: str
        Expiry date for options
    min_sp: float
        Min strike to consider
    max_sp: float
        Max strike to consider
    raw:bool
        Flag to display raw data
    export: str
        Format to export file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """
    option_chain = nasdaq_model.get_chain_given_expiration(symbol, expiry)
    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "oi_nasdaq",
        option_chain,
    )
    current_price = nasdaq_model.get_last_price(symbol)

    if min_sp == -1:
        min_strike = 0.75 * current_price
    else:
        min_strike = min_sp

    if max_sp == -1:
        max_strike = 1.25 * current_price
    else:
        max_strike = max_sp

    if external_axes is None:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=cfp.PLOT_DPI)
    elif is_valid_axes_count(external_axes, 1):
        (ax,) = external_axes
    else:
        return
    ax.plot(
        option_chain.strike,
        option_chain["c_Volume"] / 1000,
        ls="-",
        marker="o",
        label="Calls",
    )
    ax.plot(
        option_chain.strike,
        option_chain["p_Volume"] / 1000,
        ls="-",
        marker="o",
        label="Puts",
    )

    ax.axvline(current_price, lw=2, ls="--", label="Current Price", alpha=0.7)
    ax.set_xlabel("Strike Price")
    ax.set_ylabel("Volume (1k) ")
    ax.set_xlim(min_strike, max_strike)
    ax.legend(loc="best", fontsize="x-small")
    ax.set_title(f"Volume for {symbol.upper()} expiring {expiry}")

    theme.style_primary_axis(ax)
    if external_axes is None:
        theme.visualize_output()

    if raw:
        to_print = option_chain[["c_Volume", "strike", "p_Volume"]]

        print_rich_table(
            to_print[(to_print.strike < max_strike) & (to_print.strike > min_strike)],
            headers=to_print.columns,
            title=f"Volume for {symbol} expiring on {expiry}.",
        )


@log_start_end(log=logger)
def display_volume_and_oi(
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
    symbol: str
        Ticker symbol
    expiry: str
        Expiry date for options
    min_sp: float
        Min strike to consider
    max_sp: float
        Max strike to consider
    raw:bool
        Flag to display raw data
    export: str
        Format to export file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """
    option_chain = nasdaq_model.get_chain_given_expiration(symbol, expiry)
    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "voi_nasdaq",
        option_chain,
    )
    current_price = nasdaq_model.get_last_price(symbol)

    if min_sp == -1:
        min_strike = 0.75 * current_price
    else:
        min_strike = min_sp

    if max_sp == -1:
        max_strike = 1.25 * current_price
    else:
        max_strike = max_sp

    if raw:
        to_print = option_chain[
            ["c_Openinterest", "c_Volume", "strike", "p_Volume", "p_Openinterest"]
        ]

        print_rich_table(
            to_print[(to_print.strike < max_strike) & (to_print.strike > min_strike)],
            headers=to_print.columns,
            title=f"Volume and Open Interest for {symbol} expiring on {expiry}.",
        )

    option_chain = option_chain.copy()[
        ["c_Volume", "c_Openinterest", "strike", "p_Openinterest", "p_Volume"]
    ]
    option_chain[["p_Openinterest", "p_Volume"]] = (
        option_chain[["p_Openinterest", "p_Volume"]] * -1 / 1000
    )
    option_chain[["c_Openinterest", "c_Volume"]] = (
        option_chain[["c_Openinterest", "c_Volume"]] / 1000
    )

    if external_axes is None:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=cfp.PLOT_DPI)
    elif is_valid_axes_count(external_axes, 1):
        (ax,) = external_axes
    else:
        return

    ax.bar(
        option_chain.strike,
        option_chain.c_Openinterest,
        color="green",
        label="Calls: OI",
    )
    ax.bar(
        option_chain.strike,
        option_chain.c_Volume,
        color="lightgreen",
        label="Calls: Vol",
    )

    ax.bar(
        option_chain.strike, option_chain.p_Openinterest, color="red", label="Puts: OI"
    )
    ax.bar(option_chain.strike, option_chain.p_Volume, color="pink", label="Puts:Vol")

    ax.axvline(
        current_price, lw=2, ls="--", label=f"Current Price: {current_price}", alpha=0.7
    )
    ax.set_xlabel("Strike Price")
    ax.set_ylabel("Volume or OI (1k)")
    ax.set_xlim(min_strike, max_strike)
    ax.legend(loc="best", fontsize="xx-small")
    ax.set_title(f"Volume and Open Interest for {symbol.upper()} expiring {expiry}")

    theme.style_primary_axis(ax)
    if external_axes is None:
        theme.visualize_output()


@log_start_end(log=logger)
def display_chains(symbol: str, expiry: str, export: str = ""):
    """Display option chain for given expiration

    Parameters
    ----------
    symbol: str
        Ticker symbol
    expiry: str
        Expiry date for options
    export: str
        Format to export data
    """
    option_chain = nasdaq_model.get_chain_given_expiration(symbol, expiry)
    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "chain_nasdaq",
        option_chain,
    )

    print_rich_table(option_chain, headers=option_chain.columns)
