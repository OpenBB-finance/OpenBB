"""Keys view"""
__docformat__ = "numpy"

import logging
import os
from typing import Optional

from openbb_terminal import keys_model
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_keys(
    show: bool = False, export: str = "", sheet_name: Optional[str] = None
):
    """Display currently set API keys.

    Parameters
    ----------
        show: bool
            Flag to choose whether to show actual keys or not.
            By default, False.
        export : str
            Export dataframe data to csv,json,xlsx file
    """

    df = keys_model.get_keys(show=show)
    if df.empty:
        console.print("No keys available\n")
        return

    print_rich_table(
        df,
        show_index=True,
        index_name="API",
        title="Current keys",
        export=bool(export),
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "mykeys",
        df,
        sheet_name,
    )
