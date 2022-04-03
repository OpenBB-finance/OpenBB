"""Substack View"""
__docformat__ = "numpy"


import logging
import os

from openbb_terminal.cryptocurrency.defi import substack_model
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_newsletters(top: int = 10, export: str = "") -> None:
    """Display DeFi related substack newsletters.
    [Source: substack.com]

    Parameters
    ----------
    top: int
        Number of records to display
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = substack_model.get_newsletters()
    df_data = df.copy()

    print_rich_table(
        df.head(top),
        headers=list(df.columns),
        show_index=False,
        title="Substack Newsletters",
    )
    console.print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "newsletter",
        df_data,
    )
