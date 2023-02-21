"""Syncretistm View module"""
__docformat__ = "numpy"

import configparser
import logging
import os
from typing import List, Optional, Union

import matplotlib.pyplot as plt

from openbb_terminal import config_plot as cfp
from openbb_terminal.config_terminal import theme
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    export_data,
    is_valid_axes_count,
    plot_autoscale,
    print_rich_table,
)
from openbb_terminal.rich_config import console
from openbb_terminal.stocks.options.screen import syncretism_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def view_available_presets(preset: str):
    """View available presets.

    Parameters
    ----------
    preset: str
        Chosen preset
    """
    if preset:
        preset_filter = configparser.RawConfigParser()
        preset_filter.optionxform = str  # type: ignore
        preset_choices = syncretism_model.get_preset_choices()
        preset_filter.read(preset_choices[preset])
        filters_headers = ["FILTER"]

        for i, filter_header in enumerate(filters_headers):
            console.print(f" - {filter_header} -")
            d_filters = {**preset_filter[filter_header]}
            d_filters = {k: v for k, v in d_filters.items() if v}

            if d_filters:
                max_len = len(max(d_filters, key=len)) + 2
                for key, value in d_filters.items():
                    console.print(f"{key}{(max_len-len(key))*' '}: {value}")

            if i < len(filters_headers) - 1:
                console.print("\n")

    else:
        console.print("Please provide a preset template.")


@log_start_end(log=logger)
def view_screener_output(
    preset: str,
    limit: int = 20,
    export: str = "",
    sheet_name: Optional[str] = None,
) -> List:
    """Print the output of screener

    Parameters
    ----------
    preset: str
        Chosen preset
    limit: int
        Number of randomly sorted rows to display
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Format for export file

    Returns
    -------
    List
        List of tickers screened
    """
    df_res, error_msg = syncretism_model.get_screener_output(preset)
    if error_msg:
        console.print(error_msg, "\n")
        return []

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "scr",
        df_res,
        sheet_name,
    )

    if limit > 0:
        df_res = df_res.head(limit)

    print_rich_table(
        df_res, headers=list(df_res.columns), show_index=False, title="Screener Output"
    )

    return list(set(df_res["S"].values.tolist()))


# pylint:disable=too-many-arguments


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
    df = syncretism_model.get_historical_greeks(symbol, expiry, strike, chain_id, put)
    if df is None:
        return
    if df.empty:
        return

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
    ax.set_title(
        f"{(greek).capitalize()} historical for {symbol.upper()} {strike} {['Call','Put'][put]}"
    )
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
