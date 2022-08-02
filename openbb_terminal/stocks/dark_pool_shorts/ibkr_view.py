""" Interactive Broker View """
__docformat__ = "numpy"

import logging
import os

from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table
from openbb_terminal.rich_config import console
from openbb_terminal.stocks.dark_pool_shorts import ibkr_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_cost_to_borrow(num_stocks: int, export: str):
    """Display stocks with highest cost to borrow. [Source: Interactive Broker]

    Parameters
    ----------
    num_stocks: int
        Number of stocks to display
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    df = ibkr_model.get_cost_to_borrow().head(num_stocks)

    if df.empty:
        console.print("No data found.")
    else:
        print_rich_table(
            df,
            headers=list(df.columns),
            show_index=False,
            title="Highest Cost to Borrow",
        )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "cost_to_borrow",
        df,
    )
