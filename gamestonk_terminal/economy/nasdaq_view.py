"""NASDAQ Data Link View"""
__docformat__ = "numpy"

import logging
import os
from typing import List

import matplotlib.pyplot as plt
import pandas as pd

from gamestonk_terminal import feature_flags as gtff
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
def display_big_mac_index(
    country_codes: List[str], raw: bool = False, export: str = ""
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
        fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
        big_mac.plot(ax=ax, marker="o")
        ax.legend(bbox_to_anchor=(1, 1))
        ax.set_title("Big Mac Index (USD)")
        ax.set_ylabel("Price of Big Mac in USD")
        ax.grid("on")
        if gtff.USE_ION:
            plt.ion()
        fig.tight_layout()
        plt.show()

        if raw:
            print_rich_table(
                big_mac, headers=list(big_mac.columns), title="Big Mac Index"
            )

        export_data(
            export, os.path.dirname(os.path.abspath(__file__)), "bigmac", big_mac
        )
        console.print("")
    else:
        console.print("[red]Unable to get big mac data[/red]\n")
