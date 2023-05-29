import logging
import os
from typing import List, Optional

from openbb_terminal.decorators import check_api_key, log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table
from openbb_terminal.rich_config import console
from openbb_terminal.stocks import stocks_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
@check_api_key(["API_KEY_FINANCIALMODELINGPREP"])
def display_quote(
    symbols: List[str], export: str = "", sheet_name: Optional[str] = None
):
    """Financial Modeling Prep ticker(s) quote.

    Parameters
    ----------
    symbols : List[str]
        A list of ticker symbols.
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Format to export data

    Examples
    --------
    This end point displays the results as an interactive table.

    >>> from openbb_terminal.sdk import openbb
    >>> openbb.stocks.quote_chart(["MSFT"])

    Multiple tickers are retrieved at once using a comma-separated list.

    >>> openbb.stocks.quote_chart(["MSFT","AAPL"])
    """

    quote = stocks_model.get_quote(symbols)
    if quote.empty:
        console.print("[red]Data not found[/red]\n")
        return
    print_rich_table(
        quote,
        headers=quote.columns,
        title="Quote",
        index_name="Info",
        show_index=True,
        export=bool(export),
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "quote",
        quote,
        sheet_name,
    )
