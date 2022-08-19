"""Shroom view"""
__docformat__ = "numpy"

import os
from typing import List, Optional

import matplotlib
import numpy as np
import pandas as pd
from matplotlib import dates as mdates
from matplotlib import pyplot as plt
from matplotlib import ticker
from matplotlib.lines import Line2D

from openbb_terminal.config_terminal import theme
from .shroom_model import get_daily_transactions
from openbb_terminal.decorators import check_api_key
from openbb_terminal import config_plot as cfgPlot
from openbb_terminal.cryptocurrency.due_diligence.glassnode_model import (
    get_active_addresses,
    get_close_price,
    get_exchange_balances,
    get_exchange_net_position_change,
    get_hashrate,
    get_non_zero_addresses,
)
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    export_data,
    plot_autoscale,
    is_valid_axes_count,
)


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
    df = get_daily_transactions(["DAI", "USDT", "UST", "BUSD", "USDC"])
    if df.empty:
        return

    # This plot has 1 axis
    if not external_axes:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=cfgPlot.PLOT_DPI)
    elif is_valid_axes_count(external_axes, 1):
        (ax,) = external_axes
    else:
        return

    for name in ["DAI", "USDT", "BUSD", "USDC"]:
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
