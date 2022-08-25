"""Shroom view"""
__docformat__ = "numpy"

import logging
import os
from typing import List, Optional

from matplotlib import pyplot as plt

from openbb_terminal.config_terminal import theme
from .shroom_model import get_daily_transactions, get_dapp_stats
from openbb_terminal.decorators import check_api_key
from openbb_terminal import config_plot as cfgPlot
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    export_data,
    plot_autoscale,
    is_valid_axes_count,
)

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
@check_api_key(["API_SHROOM_KEY"])
def display_daily_transactions(
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Get daily transactions for certain symbols in ethereum blockchain
    [Source: https://sdk.flipsidecrypto.xyz/shroomdk]

    Parameters
    ----------

    export : str
        Export dataframe data to csv,json,xlsx file
    """
    symbols = ["DAI", "USDT", "BUSD", "USDC"]
    df = get_daily_transactions(symbols)
    if df.empty:
        return

    # This plot has 1 axis
    if not external_axes:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=cfgPlot.PLOT_DPI)
    elif is_valid_axes_count(external_axes, 1):
        (ax,) = external_axes
    else:
        return

    for name in symbols:
        ax.plot(df.index, df[name] / 1_000_000_000, label=name, lw=0.5)

    ax.set_title("Daily Transactions in Ethereum")
    ax.set_ylabel("Transactions [in billions]")
    ax.set_xlabel("Date")
    ax.set_xlim(df.index[0], df.index[-1])
    ax.legend()

    theme.style_primary_axis(ax)

    if not external_axes:
        theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "dt",
        df,
    )


@log_start_end(log=logger)
@check_api_key(["API_SHROOM_KEY"])
def display_dapp_stats(
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Get daily transactions for certain symbols in ethereum blockchain
    [Source: https://sdk.flipsidecrypto.xyz/shroomdk]

    Parameters
    ----------

    export : str
        Export dataframe data to csv,json,xlsx file
    """
    df = get_dapp_stats()
    print(df)
    symbols = ["DAI", "USDT", "BUSD", "USDC"]
    df = get_daily_transactions(symbols)
    if df.empty:
        return

    # This plot has 1 axis
    if not external_axes:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=cfgPlot.PLOT_DPI)
    elif is_valid_axes_count(external_axes, 1):
        (ax,) = external_axes
    else:
        return

    for name in symbols:
        ax.plot(df.index, df[name] / 1_000_000_000, label=name, lw=0.5)

    ax.set_title("Daily Transactions in Ethereum")
    ax.set_ylabel("Transactions [in billions]")
    ax.set_xlabel("Date")
    ax.set_xlim(df.index[0], df.index[-1])
    ax.legend()

    theme.style_primary_axis(ax)

    if not external_axes:
        theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "ds",
        df,
    )
