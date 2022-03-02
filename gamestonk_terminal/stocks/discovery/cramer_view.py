"""Cramer View"""
__docformat__ = "numpy"

import os
from gamestonk_terminal.helper_funcs import print_rich_table, export_data
from gamestonk_terminal.stocks.discovery import cramer_model
from gamestonk_terminal.rich_config import console


def display_cramer_daily(inverse: bool = True, export: str = ""):
    """

    Parameters
    ----------
    inverse:bool
        Flag to include inverse recommendation
    export:str
        Format to export data
    """

    recs = cramer_model.get_cramer_daily(inverse)
    if recs.empty:
        console.print("[red]Error getting request.\n[/red]")
    date = recs.Date[0]
    recs = recs.drop(columns=["Date"])
    console.print()
    print_rich_table(recs, title=f"Jim Cramer Recommendations for {date}")
    console.print()
    export_data(export, os.path.dirname(os.path.abspath(__file__)), "cramer", recs)
