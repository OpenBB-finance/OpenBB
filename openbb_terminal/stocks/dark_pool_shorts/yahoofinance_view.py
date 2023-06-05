""" Yahoo Finance View """
__docformat__ = "numpy"

import logging
import os
from typing import Optional

from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table
from openbb_terminal.rich_config import console
from openbb_terminal.stocks.dark_pool_shorts import yahoofinance_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_most_shorted(
    limit: int = 10, export: str = "", sheet_name: Optional[str] = None
):
    """Display most shorted stocks screener. [Source: Yahoo Finance]

    Parameters
    ----------
    limit: int
        Number of stocks to display
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    df = yahoofinance_model.get_most_shorted().head(limit)
    df.dropna(how="all", axis=1, inplace=True)
    df = df.replace(float("NaN"), "")

    if df.empty:
        return console.print("No data found.")

    print_rich_table(
        df,
        headers=list(df.columns),
        show_index=False,
        title="Most Shorted Stocks",
        export=bool(export),
    )

    return export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "shorted",
        df,
        sheet_name,
    )
