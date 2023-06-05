""" Finviz View """
__docformat__ = "numpy"

import logging
import os
from typing import Optional

from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table
from openbb_terminal.stocks.insider import finviz_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def last_insider_activity(
    symbol: str, limit: int = 10, export: str = "", sheet_name: Optional[str] = None
):
    """Display insider activity for a given stock ticker. [Source: Finviz]

    Parameters
    ----------
    symbol : str
        Stock ticker symbol
    limit : int
        Number of latest insider activity to display
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    df = finviz_model.get_last_insider_activity(symbol)

    if df.empty:
        return

    print_rich_table(
        df,
        headers=list(df.columns),
        show_index=True,
        title="Insider Activity",
        export=bool(export),
        limit=limit,
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "lins",
        df,
        sheet_name,
    )
