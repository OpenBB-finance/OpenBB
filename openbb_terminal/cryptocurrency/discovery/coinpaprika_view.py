"""CoinPaprika view"""
__docformat__ = "numpy"

import logging
import os

import openbb_terminal.cryptocurrency.discovery.coinpaprika_model as paprika
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_search_results(
    query: str,
    category: str = "all",
    top: int = 10,
    sortby: str = "id",
    descend: bool = False,
    export: str = "",
) -> None:
    """Search over CoinPaprika. [Source: CoinPaprika]

    Parameters
    ----------
    query: str
        Search query
    category: str
        Categories to search: currencies|exchanges|icos|people|tags|all. Default: all
    top: int
        Number of records to display
    sortby: str
        Key to sort data. The table can be sorted by every of its columns. Refer to
        CoinPaprikas API documentation (see https://api.coinpaprika.com/docs#tag/Tools/paths/~1search/get)
    descend: bool
        Flag to sort data descending
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    if category.lower() == "all":
        category = "currencies,exchanges,icos,people,tags"

    df = paprika.get_search_results(query=query, category=category)

    if df.empty:
        console.print(
            f"No results for search query '{query}' in category '{category}'\n"
        )
        return

    df = df.sort_values(by=sortby, ascending=descend)

    print_rich_table(
        df.head(top),
        headers=list(df.columns),
        show_index=False,
        title="CoinPaprika Results",
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "search",
        df,
    )
