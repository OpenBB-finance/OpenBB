""" Finviz Comparison View """
__docformat__ = "numpy"

from typing import List
import os

from tabulate import tabulate

from gamestonk_terminal.helper_funcs import export_data
from gamestonk_terminal.stocks.comparison_analysis import finviz_compare_model
from gamestonk_terminal import feature_flags as gtff


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
        print("No screened data found.")
    else:
        if gtff.USE_TABULATE_DF:
            # TODO: figure out right way to use different floatfmts across different cols
            print(
                tabulate(
                    df_screen,
                    headers=df_screen.columns,
                    showindex=False,
                    tablefmt="fancy_grid",
                )
            )
        else:
            print(df_screen.to_string())

    print("")
    export_data(
        export, os.path.dirname(os.path.abspath(__file__)), data_type, df_screen
    )
