import logging
import os
from typing import Optional

from openbb_terminal.decorators import check_api_key, log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table
from openbb_terminal.rich_config import console
from openbb_terminal.stocks import stocks_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
@check_api_key(["API_KEY_FINANCIALMODELINGPREP"])
def display_quote(symbol: str, export: str = "", sheet_name: Optional[str] = None):
    """Financial Modeling Prep ticker quote

    Parameters
    ----------
    symbol : str
        Fundamental analysis ticker symbol
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Format to export data
    """

    quote = stocks_model.get_quote(symbol)
    if quote.empty:
        console.print("[red]Data not found[/red]\n")
        return
    print_rich_table(
        quote,
        headers=["Value"],
        title=f"{symbol.upper()} Quote",
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
