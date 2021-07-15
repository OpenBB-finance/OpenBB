"""WSJ view module"""
__docformat__ = "numpy"

from tabulate import tabulate

from gamestonk_terminal.wsj_functions import (
    market_overview,
    us_bonds,
    us_indices,
    global_bonds,
    global_currencies,
    top_commodities,
)


def display_wsj(fn: str):
    """
    Display dataframe from wsj

    Parameters
    ----------
    fn: str
        What function to show
    """

    if fn == "market":
        data = market_overview()
    elif fn == "us_bonds":
        data = us_bonds()
    elif fn == "gl_bonds":
        data = global_bonds()
    elif fn == "indices":
        data = us_indices()
    elif fn == "currencies":
        data = global_currencies()
    elif fn == "commodities":
        data = top_commodities()

    print(
        tabulate(
            data,
            showindex=False,
            headers=data.columns,
            floatfmt=".2f",
            tablefmt="fancy_grid",
        )
    )
    print("")
