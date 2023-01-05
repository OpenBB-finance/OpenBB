# IMPORTATION STANDARD
import logging

# IMPORTATION THIRDPARTY
from typing import List, Optional, Tuple
import matplotlib.pyplot as plt
import pandas as pd

# IMPORTATION INTERNAL
import openbb_terminal.config_plot as cfp
from openbb_terminal.config_terminal import theme
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    is_valid_axes_count,
    plot_autoscale,
    print_rich_table,
)
from openbb_terminal.stocks.options.op_helpers import (
    Chain,
    export_options,
    calculate_max_pain,
)

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


def get_max_pain(chain: Chain) -> float:
    call_oi = chain.calls.set_index("strike")["openInterest"] / 1000
    put_oi = chain.puts.set_index("strike")["openInterest"] / 1000
    df_opt = pd.merge(call_oi, put_oi, left_index=True, right_index=True)
    df_opt = df_opt.rename(
        columns={"openInterest_x": "OI_call", "openInterest_y": "OI_put"}
    )
    return calculate_max_pain(df_opt)


def print_raw(
    chain: Chain, title: str, calls_only: bool = False, puts_only: bool = False
):
    if not puts_only:
        print_rich_table(
            chain.calls,
            headers=list(chain.calls.columns),
            show_index=False,
            title=f"{title} - Calls",
        )
    if not calls_only:
        print_rich_table(
            chain.puts,
            headers=list(chain.puts.columns),
            show_index=False,
            title=f"{title} - Puts",
        )


@log_start_end(log=logger)
def plot_vol(
    chain: Chain,
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
    chain: Chain
        Chain object
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
    """

    min_strike, max_strike = get_strikes(min_sp, max_sp, current_price)

    if external_axes is None:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=cfp.PLOT_DPI)
    elif is_valid_axes_count(external_axes, 1):
        (ax,) = external_axes
    else:
        return

    if not puts_only:
        ax.plot(
            chain.calls.strike,
            chain.calls["volume"] / 1000,
            ls="-",
            marker="o",
            label="Calls",
        )
    if not calls_only:
        ax.plot(
            chain.puts.strike,
            chain.puts["volume"] / 1000,
            ls="-",
            marker="o",
            label="Puts",
        )

    ax.axvline(current_price, lw=2, ls="--", label="Current Price", alpha=0.7)
    ax.set_xlabel("Strike Price")
    ax.set_ylabel("Volume (1k) ")
    ax.set_xlim(min_strike, max_strike)
    ax.legend(loc="best", fontsize="x-small")
    title = f"Volume for {symbol.upper()} expiring {expiry}"
    ax.set_title(title)

    theme.style_primary_axis(ax)
    if external_axes is None:
        theme.visualize_output()

    if raw:
        print_raw(chain, title, calls_only, puts_only)

    export_options(export, chain, "vol")


@log_start_end(log=logger)
def plot_oi(
    chain: Chain,
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
    chain: Chain
        Chain object
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
    """
    min_strike, max_strike = get_strikes(min_sp, max_sp, current_price)
    max_pain = get_max_pain(chain)

    if external_axes is None:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=cfp.PLOT_DPI)
    elif is_valid_axes_count(external_axes, 1):
        (ax,) = external_axes
    else:
        return

    if not puts_only:
        ax.plot(
            chain.calls.strike,
            chain.calls["openInterest"] / 1000,
            ls="-",
            marker="o",
            label="Calls",
        )
    if not calls_only:
        ax.plot(
            chain.puts.strike,
            chain.puts["openInterest"] / 1000,
            ls="-",
            marker="o",
            label="Puts",
        )

    ax.axvline(current_price, lw=2, ls="--", label="Current Price", alpha=0.7)
    ax.axvline(max_pain, lw=3, label=f"Max Pain: {max_pain}", alpha=0.7)
    ax.set_xlabel("Strike Price")
    ax.set_ylabel("Open Interest (1k) ")
    ax.set_xlim(min_strike, max_strike)
    ax.legend(loc="best", fontsize="x-small")
    title = f"Open Interest for {symbol.upper()} expiring {expiry}"
    ax.set_title(title)

    theme.style_primary_axis(ax)
    if external_axes is None:
        theme.visualize_output()

    if raw:
        print_raw(chain, title, calls_only, puts_only)

    export_options(export, chain, "oi")


@log_start_end(log=logger)
def plot_voi(
    chain: Chain,
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
    chain: Chain
        Chain object
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
    min_vol: float
        Min volume to consider
    export: str
        Format for exporting data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """
    min_strike, max_strike = get_strikes(min_sp, max_sp, current_price)
    max_pain = get_max_pain(chain)

    option_chain = pd.merge(
        chain.calls[["volume", "strike", "openInterest"]],
        chain.puts[["volume", "strike", "openInterest"]],
        on="strike",
    )

    option_chain = option_chain.rename(
        columns={
            "volume_x": "volume_call",
            "volume_y": "volume_put",
            "openInterest_x": "openInterest_call",
            "openInterest_y": "openInterest_put",
        }
    )

    option_chain[["openInterest_put", "volume_put"]] = (
        option_chain[["openInterest_put", "volume_put"]] * -1 / 1000
    )
    option_chain[["openInterest_call", "volume_call"]] = (
        option_chain[["openInterest_call", "volume_call"]] / 1000
    )

    if external_axes is None:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=cfp.PLOT_DPI)
    elif is_valid_axes_count(external_axes, 1):
        (ax,) = external_axes
    else:
        return

    ax.bar(
        option_chain.strike,
        option_chain.openInterest_call,
        color="green",
        label="Calls: OI",
    )
    ax.bar(
        option_chain.strike,
        option_chain.volume_call,
        color="lightgreen",
        label="Calls: Vol",
    )

    ax.bar(
        option_chain.strike,
        option_chain.openInterest_put,
        color="red",
        label="Puts: OI",
    )
    ax.bar(
        option_chain.strike,
        option_chain.volume_put,
        color="pink",
        label="Puts: Vol",
    )

    ax.axvline(
        current_price, lw=2, ls="--", label=f"Current Price: {current_price}", alpha=0.7
    )
    ax.axvline(max_pain, lw=2, ls="--", label=f"Max Pain: {max_pain:.2f}", alpha=0.7)
    ax.set_xlabel("Strike Price")
    ax.set_ylabel("Volume or OI (1k)")
    ax.set_xlim(min_strike, max_strike)
    ax.legend(loc="best", fontsize="xx-small")
    title = f"Volume and Open Interest for {symbol.upper()} expiring {expiry}"
    ax.set_title(title)

    theme.style_primary_axis(ax)
    if external_axes is None:
        theme.visualize_output()

    if raw:
        print_raw(chain, title)

    export_options(export, chain, "voi")
