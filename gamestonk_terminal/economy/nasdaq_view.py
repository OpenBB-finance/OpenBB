"""NASDAQ Data Link View"""
__docformat__ = "numpy"

import logging
import os
from typing import List, Optional

import matplotlib.pyplot as plt
import pandas as pd

from gamestonk_terminal.decorators import check_api_key
from gamestonk_terminal.config_terminal import theme
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.economy import nasdaq_model
from gamestonk_terminal.helper_funcs import (
    export_data,
    plot_autoscale,
    print_rich_table,
)
from gamestonk_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
@check_api_key(["API_KEY_QUANDL"])
def display_big_mac_index(
    country_codes: List[str],
    raw: bool = False,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Display Big Mac Index for given countries

    Parameters
    ----------
    country_codes : List[str]
        List of country codes to get for
    raw : bool, optional
        Flag to display raw data, by default False
    export : str, optional
        Format data, by default ""
    external_axes : Optional[List[plt.Axes]], optional
        External axes (3 axes are expected in the list), by default None
    """
    df_cols = ["Date"]
    df_cols.extend(country_codes)
    big_mac = pd.DataFrame(columns=df_cols)
    for country in country_codes:
        df1 = nasdaq_model.get_big_mac_index(country)
        if not df1.empty:
            big_mac[country] = df1["dollar_price"]
            big_mac["Date"] = df1["Date"]
    big_mac.set_index("Date", inplace=True)

    if not big_mac.empty:
        if external_axes is None:
            _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)

        else:
            if len(external_axes) != 3:
                logger.error("Expected list of 3 axis items.")
                console.print("[red]Expected list of 3 axis items./n[/red]")
                return
            (ax,) = external_axes

        big_mac.plot(ax=ax, marker="o")
        ax.legend()
        ax.set_title("Big Mac Index (USD)")
        ax.set_ylabel("Price of Big Mac in USD")
        theme.style_primary_axis(ax)
        if external_axes is None:
            theme.visualize_output()

        if raw:
            print_rich_table(
                big_mac,
                headers=list(big_mac.columns),
                title="Big Mac Index",
                show_index=True,
            )
            console.print("")

        export_data(
            export, os.path.dirname(os.path.abspath(__file__)), "bigmac", big_mac
        )
        console.print("")
    else:
        logger.error("Unable to get big mac data")
        console.print("[red]Unable to get big mac data[/red]\n")
