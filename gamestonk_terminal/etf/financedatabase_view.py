"""Finance Database view"""
__docformat__ = "numpy"

import financedatabase as fd
import pandas as pd
from tabulate import tabulate
from gamestonk_terminal import feature_flags as gtff


def show_etfs(
    category: str,
    name: str,
    description: str,
    include_exchanges: bool,
    amount: int,
    options: str,
):
    """
    Display a selection of ETFs based on category, name and/or description filtered by total assets.
    Returns the top ETFs when no argument is given. [Source: Finance Database]

    Parameters
    ----------
    category: str
        Search by category to find ETFs matching the criteria.
    name: str
        Search by name to find ETFs matching the criteria.
    description: str
        Search by description to find ETFs matching the criteria.
    include_exchanges: bool
        When you wish to include different exchanges use this boolean.
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
        data = fd.select_etfs(
            category=" ".join(category).title(), exclude_exchanges=include_exchanges
        )
    else:
        data = fd.select_etfs(category=category, exclude_exchanges=include_exchanges)

    if name is not None:
        print(name)
        data = fd.search_products(data, query=" ".join(name), search="long_name")
    if description is not None:
        data = fd.search_products(data, query=" ".join(description), search="summary")

    tabulate_data = pd.DataFrame(data).T[
        ["long_name", "family", "category", "total_assets"]
    ]
    tabulate_data_sorted = tabulate_data.sort_values(by="total_assets", ascending=False)
    tabulate_data_sorted["total_assets"] = (
        tabulate_data_sorted["total_assets [M]"] / 1e6
    )

    if gtff.USE_TABULATE_DF:
        print(
            tabulate(
                tabulate_data_sorted.iloc[:amount],
                showindex=True,
                headers=["Name", "Family", "Category", "Total Assets [M]"],
                floatfmt=".2f",
                tablefmt="fancy_grid",
            ),
            "\n",
        )
    else:
        print(tabulate_data_sorted.iloc[:amount].to_string(), "\n")
