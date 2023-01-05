# IMPORTATION STANDARD
import logging

# IMPORTATION THIRDPARTY
from typing import List, Optional, Any
import matplotlib.pyplot as plt

# IMPORTATION INTERNAL
import openbb_terminal.config_plot as cfp
from openbb_terminal.config_terminal import theme
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    is_valid_axes_count,
    plot_autoscale,
    print_rich_table,
)
from openbb_terminal.stocks.options.op_helpers import export_options

logger = logging.getLogger(__name__)

# pylint: disable=C0302,R0913


@log_start_end(log=logger)
def plot_vol(
    chain: Any,
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

    export_options(export, chain, "vol")
