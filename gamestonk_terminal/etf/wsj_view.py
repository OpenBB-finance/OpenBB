"""WSJ view"""
__docformat__ = "numpy"

import os

from tabulate import tabulate

from gamestonk_terminal.etf import wsj_model
from gamestonk_terminal.helper_funcs import (
    export_data,
)


def show_top_mover(sort_type: str, limit: int = 20, export=""):
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
    print(
        tabulate(
            data.iloc[:limit],
            showindex=False,
            headers=data.columns,
            floatfmt=".2f",
            tablefmt="fancy_grid",
        )
    )
    export_data(
        export,
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "movers"),
        sort_type,
        data,
    )
    print("")
