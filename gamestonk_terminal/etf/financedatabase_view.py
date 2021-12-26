"""Finance Database view"""
__docformat__ = "numpy"

import os
import pandas as pd
from tabulate import tabulate
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.etf import financedatabase_model
from gamestonk_terminal.helper_funcs import export_data

# pylint: disable=W0105


def display_etf_by_name(
    name: str,
    limit: int,
    export: str,
):
    """Display a selection of ETFs based on name filtered by total assets. [Source: Finance Database]

    Parameters
    ----------
    name: str
        Search by name to find ETFs matching the criteria.
    limit: int
        Limit of ETFs to display
    export: str
        Type of format to export data
    """
    data = financedatabase_model.get_etfs_by_name(name)
    if not data:
        print("No data was found with that name\n")
        return

    tabulate_data = pd.DataFrame(data).T[
        ["long_name", "family", "category", "total_assets"]
    ]
    tabulate_data_sorted = tabulate_data.sort_values(by="total_assets", ascending=False)
    tabulate_data_sorted["total_assets"] = tabulate_data_sorted["total_assets"] / 1e6

    if gtff.USE_TABULATE_DF:
        print(
            tabulate(
                tabulate_data_sorted.iloc[:limit],
                showindex=True,
                headers=["Name", "Family", "Category", "Total Assets [M]"],
                floatfmt=".2f",
                tablefmt="fancy_grid",
            ),
            "\n",
        )
    else:
        print(tabulate_data_sorted.iloc[:limit].to_string(), "\n")

    export_data(export, os.path.dirname(os.path.abspath(__file__)), "ln_fd", data)


def display_etf_by_description(
    description: str,
    limit: int,
    export: str,
):
    """Display a selection of ETFs based on description filtered by total assets. [Source: Finance Database]

    Parameters
    ----------
    description: str
        Search by description to find ETFs matching the criteria.
    limit: int
        Limit of ETFs to display
    export: str
        Type of format to export data
    """
    data = financedatabase_model.get_etfs_by_description(description)
    if not data:
        print("No data was found with that description\n")
        return

    tabulate_data = pd.DataFrame(data).T[
        ["long_name", "family", "category", "total_assets"]
    ]
    tabulate_data_sorted = tabulate_data.sort_values(by="total_assets", ascending=False)
    tabulate_data_sorted["total_assets"] = tabulate_data_sorted["total_assets"] / 1e6

    if gtff.USE_TABULATE_DF:
        print(
            tabulate(
                tabulate_data_sorted.iloc[:limit],
                showindex=True,
                headers=["Name", "Family", "Category", "Total Assets [M]"],
                floatfmt=".2f",
                tablefmt="fancy_grid",
            ),
            "\n",
        )
    else:
        print(tabulate_data_sorted.iloc[:limit].to_string(), "\n")

    export_data(export, os.path.dirname(os.path.abspath(__file__)), "ld", data)


'''
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
    tabulate_data_sorted["total_assets"] = tabulate_data_sorted["total_assets"] / 1e6

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
'''
