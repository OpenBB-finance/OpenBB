"""Finance Database view"""
__docformat__ = "numpy"

import os
import pandas as pd
from tabulate import tabulate
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.etf import financedatabase_model
from gamestonk_terminal.helper_funcs import export_data
from gamestonk_terminal.rich_config import console


def display_etf_by_name(
    name: str,
    limit: int,
    export: str = "",
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
        console.print("No data was found with that name\n")
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
        console.print(tabulate_data_sorted.iloc[:limit].to_string(), "\n")

    export_data(export, os.path.dirname(os.path.abspath(__file__)), "ln_fd", data)


def display_etf_by_description(
    description: str,
    limit: int,
    export: str = "",
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
        console.print("No data was found with that description\n")
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
        console.print(tabulate_data_sorted.iloc[:limit].to_string(), "\n")

    export_data(export, os.path.dirname(os.path.abspath(__file__)), "ld", data)


def display_etf_by_category(
    category: str,
    limit: int,
    export: str = "",
):
    """Display a selection of ETFs based on a category filtered by total assets. [Source: Finance Database]

    Parameters
    ----------
    description: str
        Search by description to find ETFs matching the criteria.
    limit: int
        Limit of ETFs to display
    export: str
        Type of format to export data
    """
    data = financedatabase_model.get_etfs_by_category(category)
    if not data:
        console.print("No data was found on that category\n")
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
        console.print(tabulate_data_sorted.iloc[:limit].to_string(), "\n")

    export_data(
        export,
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "screener"),
        "sbc",
        data,
    )
