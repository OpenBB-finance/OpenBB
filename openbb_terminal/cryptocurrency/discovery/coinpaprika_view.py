"""CoinPaprika view"""
__docformat__ = "numpy"

import logging
import os
from typing import Optional

import openbb_terminal.cryptocurrency.discovery.coinpaprika_model as paprika
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_search_results(
    query: str,
    category: str = "all",
    limit: int = 10,
    sortby: str = "id",
    ascend: bool = True,
    export: str = "",
    sheet_name: Optional[str] = None,
) -> None:
    """Prints table showing Search over CoinPaprika. [Source: CoinPaprika]

    Parameters
    ----------
    query: str
        Search query
    category: str
        Categories to search: currencies|exchanges|icos|people|tags|all. Default: all
    limit: int
        Number of records to display
    sortby: str
        Key to sort data. The table can be sorted by every of its columns. Refer to
        API documentation (see https://api.coinpaprika.com/docs#tag/Tools/paths/~1search/get)
    ascend: bool
        Flag to sort data descending
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    if category.lower() == "all":
        category = "currencies,exchanges,icos,people,tags"

    df = paprika.get_search_results(
        query=query, category=category, sortby=sortby, ascend=ascend
    )

    if df.empty:
        console.print(
            f"No results for search query '{query}' in category '{category}'\n"
        )
        return

    print_rich_table(
        df,
        headers=list(df.columns),
        show_index=False,
        title="CoinPaprika Results",
        export=bool(export),
        limit=limit,
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "search",
        df,
        sheet_name,
    )
