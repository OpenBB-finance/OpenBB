"""WSJ view"""
__docformat__ = "numpy"

import financedatabase as fd
import pandas as pd
from tabulate import tabulate


def show_etfs(category: str, name: str, description: str, amount: int, options: str):
    """
    Display a selection of ETFs based on category, name and/or description filtered by total assets.
    Returns the top ETFs when no argument is given.

    Parameters
    ----------
    category: str
        Search by category to find ETFs matching the criteria.
    name: str
        Search by name to find ETFs matching the criteria.
    description: str
        Search by description to find ETFs matching the criteria.
    amount : int
        Number of ETFs to display, default is 10.
    options : str
        Show the category options.
    """
    if options:
        for option in fd.show_options("etfs"):
            print(option)
        return

    if category is not None:
        data = fd.select_etfs(category=" ".join(category))
    else:
        data = fd.select_etfs(category=category)

    if name is not None:
        data = fd.search_products(data, query=" ".join(name), search="long_name")
    if description is not None:
        data = fd.search_products(data, query=" ".join(description), search="summary")

    tabulate_data = pd.DataFrame(data).T[
        ["long_name", "family", "category", "total_assets"]
    ]
    tabulate_data_sorted = tabulate_data.sort_values(by="total_assets", ascending=False)

    print(
        tabulate(
            tabulate_data_sorted.iloc[:amount],
            showindex=True,
            headers=["Name", "Family", "Category", "Total Assets"],
            floatfmt=".2f",
            tablefmt="fancy_grid",
        )
    )
