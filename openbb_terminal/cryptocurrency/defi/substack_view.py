"""Substack View"""
__docformat__ = "numpy"


import logging
import os
from typing import Optional

from openbb_terminal.cryptocurrency.defi import substack_model
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_newsletters(
    limit: int = 10, export: str = "", sheet_name: Optional[str] = None
) -> None:
    """Prints table showing DeFi related substack newsletters.
    [Source: substack.com]

    Parameters
    ----------
    limit: int
        Number of records to display
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = substack_model.get_newsletters()

    print_rich_table(
        df,
        headers=list(df.columns),
        show_index=False,
        title="Substack Newsletters",
        export=bool(export),
        limit=limit,
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "newsletter",
        df,
        sheet_name,
    )
