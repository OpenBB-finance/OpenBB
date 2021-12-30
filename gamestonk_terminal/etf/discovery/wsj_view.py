"""WSJ view"""
__docformat__ = "numpy"

import os

from tabulate import tabulate

from gamestonk_terminal.etf.discovery import wsj_model
from gamestonk_terminal.helper_funcs import (
    export_data,
)
from gamestonk_terminal import feature_flags as gtff


def show_top_mover(sort_type: str, limit: int = 10, export=""):
    """
     Show top ETF movers from wsj.com
     Parameters
     ----------
     sort_type: str
         What to show.  Either Gainers, Decliners or Activity
    limit: int
         Number of etfs to show
     export: str
         Format to export data
    """
    data = wsj_model.etf_movers(sort_type)
    if data.empty:
        print("No data available\n")
        return

    if gtff.USE_TABULATE_DF:
        print(
            tabulate(
                data.iloc[:limit],
                showindex=False,
                headers=data.columns,
                floatfmt=".2f",
                tablefmt="fancy_grid",
            )
        )
    else:
        print(data.head(limit).to_string())
    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        sort_type,
        data,
    )
    print("")
