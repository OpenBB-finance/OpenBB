"""NASDAQ Data Link View"""
__docformat__ = "numpy"

from typing import List
import os

import matplotlib.pyplot as plt
import pandas as pd
from tabulate import tabulate
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.economy import nasdaq_model
from gamestonk_terminal.helper_funcs import export_data, plot_autoscale
from gamestonk_terminal.config_plot import PLOT_DPI


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
        big_mac[country] = df1["dollar_price"]
        big_mac["Date"] = df1["Date"]
    big_mac.set_index("Date", inplace=True)
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
        if gtff.USE_TABULATE_DF:
            print(tabulate(big_mac, headers=big_mac.columns, tablefmt="fancy_grid"))
        else:
            print(big_mac.head(20).to_string())

    export_data(export, os.path.dirname(os.path.abspath(__file__)), "bigmac", big_mac)
    print("")
