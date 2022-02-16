""" Business Insider View """
__docformat__ = "numpy"

import logging
import os
import textwrap

from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.helper_funcs import export_data, print_rich_table
from gamestonk_terminal.rich_config import console
from gamestonk_terminal.stocks.fundamental_analysis import business_insider_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
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

    df_new = df_management.applymap(
        lambda x: "\n".join(textwrap.wrap(x, width=30)) if isinstance(x, str) else x
    )

    names = ["Name"] + list(df_new.columns)
    if not df_new.empty:
        print_rich_table(
            df_new,
            title="Company Managers",
            headers=names,
        )

        console.print("")
        export_data(
            export, os.path.dirname(os.path.abspath(__file__)), "mgmt", df_management
        )
    else:
        console.print("[red]Data not available[/red]\n")
