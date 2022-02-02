"""Syncretistm View module"""
__docformat__ = "numpy"

import configparser
import logging
import os
from typing import List

import matplotlib.pyplot as plt

from gamestonk_terminal import config_plot as cfp
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.helper_funcs import (
    export_data,
    plot_autoscale,
    print_rich_table,
)
from gamestonk_terminal.rich_config import console
from gamestonk_terminal.stocks.options import syncretism_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def view_available_presets(preset: str, presets_path: str):
    """View available presets.

    Parameters
    ----------
    preset: str
       Preset to look at
    presets_path: str
        Path to presets folder
    """
    if preset:
        preset_filter = configparser.RawConfigParser()
        preset_filter.optionxform = str  # type: ignore
        preset_filter.read(os.path.join(presets_path, preset + ".ini"))
        filters_headers = ["FILTER"]
        console.print("")

        for filter_header in filters_headers:
            console.print(f" - {filter_header} -")
            d_filters = {**preset_filter[filter_header]}
            d_filters = {k: v for k, v in d_filters.items() if v}
            if d_filters:
                max_len = len(max(d_filters, key=len)) + 2
                for key, value in d_filters.items():
                    console.print(f"{key}{(max_len-len(key))*' '}: {value}")
            console.print("")

    else:
        console.print("Please provide a preset template.")
    console.print("")


@log_start_end(log=logger)
def view_screener_output(
    preset: str, presets_path: str, n_show: int, export: str
) -> List:
    """Print the output of screener

    Parameters
    ----------
    preset: str
        Preset file to screen for
    presets_path: str
        Path to preset folder
    n_show: int
        Number of randomly sorted rows to display
    export: str
        Format for export file

    Returns
    -------
    List
        List of tickers screened
    """
    df_res, error_msg = syncretism_model.get_screener_output(preset, presets_path)
    if error_msg:
        console.print(error_msg, "\n")
        return []

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "scr",
        df_res,
    )

    if n_show > 0:
        df_res = df_res.head(n_show)

    print_rich_table(
        df_res, headers=list(df_res.columns), show_index=False, title="Screener Output"
    )
    console.print("")

    return df_res["S"].values.tolist()


# pylint:disable=too-many-arguments


@log_start_end(log=logger)
def view_historical_greeks(
    ticker: str,
    expiry: str,
    strike: float,
    greek: str,
    chain_id: str,
    put: bool,
    raw: bool,
    n_show: int,
    export: str = "",
):
    """Plots historical greeks for a given option

    Parameters
    ----------
    ticker: str
        Stock ticker
    expiry: str
        Expiration date
    strike: float
        Strike price to consider
    greek: str
        Greek variable to plot
    chain_id: str
        OCC option chain.  Overwrites other variables
    put: bool
        Is this a put option?
    raw: bool
        Print to console
    n_show: int
        Number of rows to show in raw
    export: str
        Format to export data
    """
    df = syncretism_model.get_historical_greeks(ticker, expiry, chain_id, strike, put)

    if raw:
        print_rich_table(
            df.tail(n_show), headers=list(df.columns), title="Historical Greeks"
        )

    fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=cfp.PLOT_DPI)
    im1 = ax.plot(df.index, df[greek], c="firebrick", label=greek)
    ax.set_ylabel(greek)
    ax1 = ax.twinx()
    im2 = ax1.plot(df.index, df.price, c="dodgerblue", label="Stock Price")
    ax1.set_ylabel(f"{ticker} Price")
    ax1.set_xlabel("Date")
    ax.grid("on")
    ax.set_title(
        f"{greek} historical for {ticker.upper()} {strike} {['Call','Put'][put]}"
    )
    plt.gcf().autofmt_xdate()

    if gtff.USE_ION:
        plt.ion()

    ims = im1 + im2
    labels = [lab.get_label() for lab in ims]
    plt.legend(ims, labels, loc=0)
    fig.tight_layout(pad=1)
    plt.show()
    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "grhist",
        df,
    )
    console.print("")
