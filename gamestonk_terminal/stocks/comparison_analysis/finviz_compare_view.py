""" Finviz Comparison View """
__docformat__ = "numpy"

from typing import List
import os

from gamestonk_terminal.helper_funcs import export_data, print_rich_table
from gamestonk_terminal.stocks.comparison_analysis import finviz_compare_model
from gamestonk_terminal.rich_config import console


def screener(similar: List[str], data_type: str, export: str = ""):
    """Screener

    Parameters
    ----------
    similar : List[str]
        Similar companies to compare income with
    data_type : str
        Screener to use.  One of {overview, valuation, financial, ownership, performance, technical}
    export : str
        Format to export data
    """
    df_screen = finviz_compare_model.get_comparison_data(data_type, similar)

    if df_screen.empty:
        console.print("No screened data found.")
    else:
        print_rich_table(
            df_screen,
            headers=list(df_screen.columns),
            show_index=False,
            title="Stock Screener",
        )

    console.print("")
    export_data(
        export, os.path.dirname(os.path.abspath(__file__)), data_type, df_screen
    )
