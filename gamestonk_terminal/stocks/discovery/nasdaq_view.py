"""NASDAQ DataLink View"""
__docformat__ = "numpy"

import os

from colorama import Style
from tabulate import tabulate

from gamestonk_terminal.helper_funcs import export_data
from gamestonk_terminal.stocks.discovery import nasdaq_model
import gamestonk_terminal.feature_flags as gtff
from gamestonk_terminal.rich_config import console


def display_top_retail(n_days: int = 3, export: str = ""):
    """Display the top 10 retail traded stocks for last days

    Parameters
    ----------
    n_days : int, optional
        Number of days to show by default 3
    export : str, optional
        Format to export data, by default ""
    """
    retails = nasdaq_model.get_retail_tickers()
    for date, df in retails.head(n_days * 10).groupby("Date"):
        console.print(f"{Style.BRIGHT}{date} Top Retail:{Style.RESET_ALL}")
        df = df.drop(columns=["Date"])
        if gtff.USE_TABULATE_DF:
            print(
                tabulate(
                    df.reset_index(drop=True),
                    headers=df.columns[1:],
                    showindex=False,
                    tablefmt="fancy_grid",
                )
            )
        else:
            console.print(df.reset_index(drop=True).to_string(index=False))

        console.print("")
    export_data(export, os.path.dirname(os.path.abspath(__file__)), "rtat", retails)
