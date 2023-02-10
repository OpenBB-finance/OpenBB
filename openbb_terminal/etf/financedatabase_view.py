"""Finance Database view"""
__docformat__ = "numpy"

import logging
import os
from typing import Optional

import pandas as pd

from openbb_terminal.decorators import log_start_end
from openbb_terminal.etf import financedatabase_model
from openbb_terminal.helper_funcs import export_data, print_rich_table
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_etf_by_name(
    name: str,
    limit: int = 10,
    export: str = "",
    sheet_name: Optional[str] = None,
):
    """Display a selection of ETFs based on name filtered by total assets. [Source: Finance Database]

    Parameters
    ----------
    name: str
        Search by name to find ETFs matching the criteria.
    limit: int
        Limit of ETFs to display
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Type of format to export data
    """
    data = financedatabase_model.get_etfs_by_name(name)
    if not data:
        console.print("No data was found with that name\n")
        return

    table_data = pd.DataFrame(data).T[
        ["long_name", "family", "category", "total_assets"]
    ]

    # Sort by total assets but it is then dropped due to not being completely up to date
    table_data_sorted = table_data.sort_values(by="total_assets", ascending=False)
    table_data_sorted = table_data_sorted.drop("total_assets", axis=1)

    print_rich_table(
        table_data_sorted.iloc[:limit],
        show_index=True,
        headers=["Name", "Family", "Category"],
        title="ETFs by Total Assets",
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "ln_fd",
        table_data_sorted,
        sheet_name,
    )


@log_start_end(log=logger)
def display_etf_by_description(
    description: str,
    limit: int = 10,
    export: str = "",
    sheet_name: Optional[str] = None,
):
    """Display a selection of ETFs based on description filtered by total assets.
    [Source: Finance Database]

    Parameters
    ----------
    description: str
        Search by description to find ETFs matching the criteria.
    limit: int
        Limit of ETFs to display
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Type of format to export data
    """
    data = financedatabase_model.get_etfs_by_description(description)
    if not data:
        console.print("No data was found with that description\n")
        return

    table_data = pd.DataFrame(data).T[
        ["long_name", "family", "category", "total_assets"]
    ]
    # Sort by total assets but it is then dropped due to not being completely up to date
    table_data_sorted = table_data.sort_values(by="total_assets", ascending=False)
    table_data_sorted = table_data_sorted.drop("total_assets", axis=1)

    print_rich_table(
        table_data_sorted.iloc[:limit],
        show_index=True,
        headers=["Name", "Family", "Category"],
        title="ETFs by Total Assets",
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "ld",
        data,
        sheet_name,
    )


@log_start_end(log=logger)
def display_etf_by_category(
    category: str,
    limit: int = 10,
    export: str = "",
    sheet_name: Optional[str] = None,
):
    """Display a selection of ETFs based on a category filtered by total assets.
    [Source: Finance Database]

    Parameters
    ----------
    description: str
        Search by description to find ETFs matching the criteria.
    limit: int
        Limit of ETFs to display
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Type of format to export data
    """
    data = financedatabase_model.get_etfs_by_category(category)
    if not data:
        console.print("No data was found on that category\n")
        return

    table_data = pd.DataFrame(data).T[
        ["long_name", "family", "category", "total_assets"]
    ]
    # Sort by total assets but it is then dropped due to not being completely up to date
    table_data_sorted = table_data.sort_values(by="total_assets", ascending=False)
    table_data_sorted = table_data_sorted.drop("total_assets", axis=1)

    print_rich_table(
        table_data_sorted.iloc[:limit],
        show_index=True,
        headers=["Name", "Family", "Category"],
        title="ETFs by Category and Total Assets",
    )

    export_data(
        export,
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "screener"),
        "sbc",
        data,
        sheet_name,
    )
