"""CoinMarketCap view"""
__docformat__ = "numpy"

import logging
import os
from typing import Optional

from openbb_terminal.cryptocurrency.discovery import coinmarketcap_model
from openbb_terminal.decorators import check_api_key, log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
@check_api_key(["API_CMC_KEY"])
def display_cmc_top_coins(
    limit: int = 15,
    sortby: str = "CMC_Rank",
    ascend: bool = True,
    export: str = "",
    sheet_name: Optional[str] = None,
) -> None:
    """Prints table showing top n coins. [Source: CoinMarketCap]

    Parameters
    ----------
    limit: int
        Number of records to display
    sortby: str
        Key to sort data. The table can be sorted by every of its columns. Refer to
        Coin Market Cap:s API documentation, see:
        https://coinmarketcap.com/api/documentation/v1/#operation/getV1CryptocurrencyListingsLatest
    ascend: bool
        Flag to sort data ascending
    export : str
        Export dataframe data to csv,json,xlsx file

    """

    df = coinmarketcap_model.get_cmc_top_n(sortby, ascend)

    if df.empty:
        console.print("No Data Found\n")
        return

    print_rich_table(
        df,
        headers=list(df.columns),
        show_index=False,
        title="Top Coins",
        export=bool(export),
        limit=limit,
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "cmctop",
        df,
        sheet_name,
    )
