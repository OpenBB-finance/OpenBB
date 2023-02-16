"""Intrinio View Functions"""
__docformat__ = "numpy"

import logging
import os
from typing import List, Optional, Union

import matplotlib.pyplot as plt
import mplfinance as mpf

from openbb_terminal import config_plot as cfp
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
from openbb_terminal.stocks.options import intrinio_model

logger = logging.getLogger(__name__)

# pylint: disable=too-many-arguments


@log_start_end(log=logger)
def display_historical(
    symbol: str,
    expiry: str,
    strike: float = 0,
    put: bool = False,
    raw: bool = False,
    chain_id: Optional[str] = None,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: Optional[List[plt.Axes]] = None,
) -> None:
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
    sheet_name: str
        Optionally specify the name of the sheet to export to
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is ex"""

    if chain_id is not None:
        df_hist = intrinio_model.get_historical_options(chain_id)
        title = f"{chain_id} Historical"
    else:
        chain_id = f"{symbol}{''.join(expiry[2:].split('-'))}{'P' if put else 'C'}{str(int(1000*strike)).zfill(8)}"
        df_hist = intrinio_model.get_historical_options(chain_id)
        title = f"{symbol} {expiry} {strike} {['Call', 'Put'][put]} Historical"

    if raw:
        print_rich_table(
            df_hist,
            headers=[x.title() for x in df_hist.columns],
            title="Historical Option Prices",
        )

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
            title,
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

    if export:
        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "hist",
            df_hist,
            sheet_name,
        )


@log_start_end(log=logger)
def view_historical_greeks(
    symbol: str,
    expiry: str,
    strike: Union[float, str],
    greek: str = "Delta",
    chain_id: str = "",
    put: bool = False,
    raw: bool = False,
    limit: Union[int, str] = 20,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Plots historical greeks for a given option. [Source: Syncretism]

    Parameters
    ----------
    symbol: str
        Stock ticker
    expiry: str
        Expiration date
    strike: Union[str, float]
        Strike price to consider
    greek: str
        Greek variable to plot
    chain_id: str
        OCC option chain.  Overwrites other variables
    put: bool
        Is this a put option?
    raw: bool
        Print to console
    limit: int
        Number of rows to show in raw
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """

    if chain_id:
        df = intrinio_model.get_historical_options(chain_id)
        title = f"{(greek).capitalize()} historical for {chain_id}"
    else:
        chain_id = f"{symbol}{''.join(expiry[2:].split('-'))}{'P' if put else 'C'}{str(int(1000*strike)).zfill(8)}"
        df = intrinio_model.get_historical_options(chain_id)
        title = f"{(greek).capitalize()} historical for {symbol.upper()} {strike} {['Call','Put'][put]}"

    if df.empty:
        return

    df = df.rename(columns={"impliedVolatility": "iv", "close": "price"})

    if isinstance(limit, str):
        try:
            limit = int(limit)
        except ValueError:
            console.print(
                f"[red]Could not convert limit of {limit} to a number.[/red]\n"
            )
            return
    if raw:
        print_rich_table(
            df.tail(limit),
            headers=list(df.columns),
            title="Historical Greeks",
            show_index=True,
        )

    if not external_axes:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=cfp.PLOT_DPI)
    elif is_valid_axes_count(external_axes, 1):
        (ax,) = external_axes
    else:
        return

    try:
        greek_df = df[greek.lower()]
    except KeyError:
        console.print(f"[red]Could not find greek {greek} in data.[/red]\n")
        return
    im1 = ax.plot(df.index, greek_df, label=greek.title(), color=theme.up_color)
    ax.set_ylabel(greek)
    ax1 = ax.twinx()
    im2 = ax1.plot(df.index, df.price, label="Stock Price", color=theme.down_color)
    ax1.set_ylabel(f"{symbol} Price")
    ax.set_title(title)
    if df.empty:
        console.print("[red]Data from API is not valid.[/red]\n")
        return
    ax.set_xlim(df.index[0], df.index[-1])
    ims = im1 + im2
    labels = [lab.get_label() for lab in ims]

    ax.legend(ims, labels, loc=0)
    theme.style_twin_axes(ax, ax1)

    if not external_axes:
        theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "grhist",
        df,
        sheet_name,
    )
