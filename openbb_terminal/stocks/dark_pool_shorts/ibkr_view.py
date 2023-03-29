""" Interactive Broker View """
__docformat__ = "numpy"

import logging
import os
from typing import Optional

from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table
from openbb_terminal.rich_config import console
from openbb_terminal.stocks.dark_pool_shorts import ibkr_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_cost_to_borrow(
    limit: int = 20, export: str = "", sheet_name: Optional[str] = None
):
    """Display stocks with highest cost to borrow. [Source: Interactive Broker]

    Parameters
    ----------
    limit: int
        Number of stocks to display
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    df = ibkr_model.get_cost_to_borrow().head(limit)

    if df.empty:
        return console.print("No data found.")

    print_rich_table(
        df,
        headers=list(df.columns),
        show_index=False,
        title="Highest Cost to Borrow",
        export=bool(export),
    )

    return export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "cost_to_borrow",
        df,
        sheet_name,
    )
