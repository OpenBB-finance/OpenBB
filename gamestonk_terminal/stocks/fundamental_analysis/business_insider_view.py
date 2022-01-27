""" Business Insider View """
__docformat__ = "numpy"

import os
import textwrap

from gamestonk_terminal.helper_funcs import export_data, print_rich_table
from gamestonk_terminal.stocks.fundamental_analysis import business_insider_model
from gamestonk_terminal.rich_config import console


def display_management(ticker: str, export: str = ""):
    """Display company's managers

    Parameters
    ----------
    ticker : str
        Stock ticker
    export : str
        Format to export data
    """
    df_management = business_insider_model.get_management(ticker)

    names = ["Name"] + list(df_management.columns)

    print_rich_table(
        df_management.applymap(
            lambda x: "\n".join(textwrap.wrap(x, width=30)) if isinstance(x, str) else x
        ),
        title="Company Managers",
        headers=names,
    )

    console.print("")
    export_data(
        export, os.path.dirname(os.path.abspath(__file__)), "mgmt", df_management
    )
