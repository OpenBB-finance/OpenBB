"""Chartexchange view"""
__docformat__ = "numpy"

import logging
import os
from typing import List, Optional

import matplotlib.pyplot as plt
import mplfinance as mpf
import pandas as pd

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
from openbb_terminal.stocks.options import chartexchange_model

logger = logging.getLogger(__name__)

# pylint: disable=too-many-arguments


@log_start_end(log=logger)
def plot_chart(
    df: pd.DataFrame,
    candle_chart_kwargs: dict,
    option_type: str,
    symbol: str,
    external_axes: Optional[List[plt.Axes]] = None,
):
    if not external_axes:
        candle_chart_kwargs["returnfig"] = True
        candle_chart_kwargs["figratio"] = (10, 7)
        candle_chart_kwargs["figscale"] = 1.10
        candle_chart_kwargs["figsize"] = plot_autoscale()
        fig, ax = mpf.plot(df, **candle_chart_kwargs)
        fig.suptitle(
            f"Historical quotes for {symbol} {option_type}",
            x=0.055,
            y=0.965,
            horizontalalignment="left",
        )
        lambda_long_number_format_y_axis(df, "Volume", ax)
        theme.visualize_output(force_tight_layout=False)
        ax[0].legend()
    elif is_valid_axes_count(external_axes, 1):
        (ax1,) = external_axes
        candle_chart_kwargs["ax"] = ax1
        mpf.plot(df, **candle_chart_kwargs)
    else:
        return


@log_start_end(log=logger)
def display_raw(
    symbol: str = "GME",
    expiry: str = "2021-02-05",
    call: bool = True,
    price: float = 90,
    limit: int = 10,
    chain_id: Optional[str] = None,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: Optional[List[plt.Axes]] = None,
) -> None:
    """Return raw stock data[chartexchange]

    Parameters
    ----------
    symbol : str
        Ticker symbol for the given option
    expiry : str
        The expiry of expiration, format "YYYY-MM-DD", i.e. 2010-12-31.
    call : bool
        Whether the underlying asset should be a call or a put
    price : float
        The strike of the expiration
    limit : int
        Number of rows to show
    chain_id: str
        Optional chain id instead of ticker and expiry and strike
    export : str
        Export data as CSV, JSON, XLSX
    external_axes: Optional[List[plt.Axes]]
        External axes (1 axis is expected in the list), by default None
    """

    df = chartexchange_model.get_option_history(symbol, expiry, call, price, chain_id)[
        ::-1
    ]
    if df.empty:
        console.print("[red]No data found[/red]\n")
        return
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.set_index("Date")

    candle_chart_kwargs = {
        "type": "candle",
        "style": theme.mpf_style,
        "volume": True,
        "xrotation": theme.xticks_rotation,
        "scale_padding": {"left": 0.3, "right": 1, "top": 0.8, "bottom": 0.8},
        "update_width_config": {
            "candle_linewidth": 0.6,
            "candle_width": 0.8,
            "volume_linewidth": 0.8,
            "volume_width": 0.8,
        },
        "warn_too_much_data": 10000,
        "datetime_format": "%Y-%b-%d",
    }
    # This plot has 2 axes
    option_type = "call" if call else "put"

    plot_chart(
        df=df,
        candle_chart_kwargs=candle_chart_kwargs,
        option_type=option_type,
        symbol=symbol,
        external_axes=external_axes,
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "hist",
        df,
        sheet_name,
    )
    print_rich_table(
        df.head(limit),
        headers=list(df.columns),
        show_index=True,
        title=f"{symbol.upper()} raw data",
    )
