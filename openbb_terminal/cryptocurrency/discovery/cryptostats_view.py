"""CryptoStats view"""
__docformat__ = "numpy"

import logging
import os
from typing import Optional

from openbb_terminal.cryptocurrency.discovery import cryptostats_model
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_fees(
    marketcap: bool,
    tvl: bool,
    date: str,
    limit: int = 15,
    sortby: str = "",
    ascend: bool = True,
    sheet_name: Optional[str] = None,
    export: str = "",
) -> None:
    """Display crypto with most fees paid [Source: CryptoStats]

    Parameters
    ----------
    marketcap: bool
        Flag to include marketcap
    date: str
        Date to get data from (YYYY-MM-DD)
    limit: int
        Number of records to display
    sortby: str
        Key to sort data.
    ascend: bool
        Flag to sort data ascending
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = cryptostats_model.get_fees(marketcap, tvl, date)

    if df.empty:
        console.print("No Data Found\n")
        return

    if sortby:
        df = df.sort_values(sortby, ascending=ascend)

    if "One Day Fees" in df.columns:
        one_day_fees = df.pop("One Day Fees")
        df.insert(len(df.columns), "One Day Fees", one_day_fees)

    print_rich_table(
        df,
        headers=list(df.columns),
        show_index=False,
        title="Crypto Fees",
        limit=limit,
    )

    export_data(
        export, os.path.dirname(os.path.abspath(__file__)), "fees", df, sheet_name
    )
