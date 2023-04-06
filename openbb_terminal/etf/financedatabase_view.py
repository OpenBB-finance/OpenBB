"""Finance Database view"""
__docformat__ = "numpy"

import logging
import os
from typing import Optional

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
    """Display a selection of ETFs based on name. [Source: Finance Database]

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

    if data.empty:
        console.print("No data was found with that name.")
        return

    table_data = data[["name", "family", "category_group", "category"]]

    print_rich_table(
        table_data,
        show_index=True,
        headers=["Name", "Family", "Category Group", "Category"],
        title="ETFs",
        export=bool(export),
        limit=limit,
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "ln_fd",
        table_data,
        sheet_name,
    )


@log_start_end(log=logger)
def display_etf_by_description(
    description: str,
    limit: int = 10,
    export: str = "",
    sheet_name: Optional[str] = None,
):
    """Display a selection of ETFs based on description. [Source: Finance Database]

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

    if data.empty:
        console.print("No data was found with that description.")
        return

    table_data = data[["name", "family", "category_group", "category"]]

    print_rich_table(
        table_data,
        show_index=True,
        headers=["Name", "Family", "Category Group", "Category"],
        title="ETFs",
        export=bool(export),
        limit=limit,
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "ld",
        table_data,
        sheet_name,
    )


@log_start_end(log=logger)
def display_etf_by_category(
    category: str,
    limit: int = 10,
    export: str = "",
    sheet_name: Optional[str] = None,
):
    """Display a selection of ETFs based on a category. [Source: Finance Database]

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

    if data.empty:
        console.print("No data was found on that category.")
        return

    table_data = data[["name", "family", "category_group", "category"]]

    print_rich_table(
        table_data,
        show_index=True,
        headers=["Name", "Family", "Category Group", "Category"],
        title="ETFs by Category",
        export=bool(export),
        limit=limit,
    )

    export_data(
        export,
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "screener"),
        "sbc",
        table_data,
        sheet_name,
    )
