"""Tradier options view"""
__docformat__ = "numpy"

import argparse
import logging
import os
import warnings
from typing import List, Optional

import matplotlib.pyplot as plt
import mplfinance as mpf

from openbb_terminal.config_terminal import theme
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    export_data,
    is_valid_axes_count,
    lambda_long_number_format_y_axis,
    plot_autoscale,
    print_rich_table,
)
from openbb_terminal.rich_config import console
from openbb_terminal.stocks.options import tradier_model

logger = logging.getLogger(__name__)

warnings.filterwarnings("ignore")


@log_start_end(log=logger)
def check_valid_option_chains_headers(headers: str) -> List[str]:
    """Check valid option chains headers

    Parameters
    ----------
    headers : str
        Option chains headers

    Returns
    -------
    List[str]
        List of columns string
    """
    columns = [str(item) for item in headers.split(",")]

    for header in columns:
        if header not in tradier_model.df_columns:
            raise argparse.ArgumentTypeError("Invalid option chains header selected!")

    return columns


@log_start_end(log=logger)
def display_historical(
    symbol: str,
    expiry: str,
    strike: float = 0,
    put: bool = False,
    raw: bool = False,
    chain_id: str = None,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Plot historical option prices

    Parameters
    ----------
    symbol: str
        Stock ticker symbol
    expiry: str
        Expiry date of option
    strike: float
        Option strike price
    put: bool
        Is this a put option?
    raw: bool
        Print raw data
    chain_id: str
        OCC option symbol
    export: str
        Format of export file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """

    df_hist = tradier_model.get_historical_options(
        symbol, expiry, strike, put, chain_id
    )

    if raw:
        print_rich_table(
            df_hist,
            headers=[x.title() for x in df_hist.columns],
            title="Historical Option Prices",
        )

    op_type = ["call", "put"][put]

    candle_chart_kwargs = {
        "type": "candle",
        "style": theme.mpf_style,
        "volume": True,
        "xrotation": theme.xticks_rotation,
        "scale_padding": {"left": 0.3, "right": 1.2, "top": 0.8, "bottom": 0.8},
        "update_width_config": {
            "candle_linewidth": 0.6,
            "candle_width": 0.8,
            "volume_linewidth": 0.8,
            "volume_width": 0.8,
        },
        "datetime_format": "%Y-%b-%d",
    }
    if external_axes is None:
        candle_chart_kwargs["returnfig"] = True
        candle_chart_kwargs["figratio"] = (10, 7)
        candle_chart_kwargs["figscale"] = 1.10
        candle_chart_kwargs["figsize"] = plot_autoscale()
        fig, ax = mpf.plot(df_hist, **candle_chart_kwargs)
        fig.suptitle(
            f"Historical {strike} {op_type.title()}",
            x=0.055,
            y=0.965,
            horizontalalignment="left",
        )
        lambda_long_number_format_y_axis(df_hist, "volume", ax)
        theme.visualize_output(force_tight_layout=False)
    elif is_valid_axes_count(external_axes, 2):
        (ax1, ax2) = external_axes
        candle_chart_kwargs["ax"] = ax1
        candle_chart_kwargs["volume"] = ax2
        mpf.plot(df_hist, **candle_chart_kwargs)
    else:
        return

    console.print()

    if export:
        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "hist",
            df_hist,
        )
