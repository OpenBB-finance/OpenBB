"""DeFi Pulse view"""
__docformat__ = "numpy"

import logging
import os

from openbb_terminal.cryptocurrency.defi import defipulse_model
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_defipulse(top: int, sortby: str, descend: bool, export: str = "") -> None:
    """Displays all DeFi Pulse crypto protocols.
    [Source: https://defipulse.com/]

    Parameters
    ----------
    top: int
        Number of records to display
    sortby: str
        Key by which to sort data
    descend: bool
        Flag to sort data descending
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = defipulse_model.get_defipulse_index()
    df_data = df.copy()

    df = df.sort_values(by=sortby, ascending=descend)

    print_rich_table(
        df.head(top),
        headers=list(df.columns),
        show_index=False,
        title="DeFi Pulse Crypto Protocols",
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "dpi",
        df_data,
    )
