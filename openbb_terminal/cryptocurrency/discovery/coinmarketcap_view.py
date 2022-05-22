"""CoinMarketCap view"""
__docformat__ = "numpy"

import logging
import os

from openbb_terminal.decorators import check_api_key
from openbb_terminal.cryptocurrency.discovery import coinmarketcap_model
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)

sort_map = {
    "Symbol": "Symbol",
    "CMC_Rank": "CMC_Rank",
    "LastPrice": "Last Price",
    "DayPctChange": "1 Day Pct Change",
    "MarketCap": "Market Cap ($B)",
}


@log_start_end(log=logger)
@check_api_key(["API_CMC_KEY"])
def display_cmc_top_coins(
    top: int = 15,
    sortby: str = "CMC_Rank",
    descend: bool = False,
    export: str = "",
) -> None:
    """Shows top n coins. [Source: CoinMarketCap]

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

    df = coinmarketcap_model.get_cmc_top_n()

    if df.empty:
        console.print("No Data Found\n")
        return

    df = df.sort_values(by=sort_map[sortby], ascending=descend)

    print_rich_table(
        df.iloc[:top, :], headers=list(df.columns), show_index=False, title="Top Coins"
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "cmctop",
        df,
    )
