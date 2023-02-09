import logging

from openbb_terminal.decorators import check_api_key, log_start_end
from openbb_terminal.helper_funcs import print_rich_table
from openbb_terminal.rich_config import console
from openbb_terminal.stocks import stocks_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
@check_api_key(["API_KEY_FINANCIALMODELINGPREP"])
def display_quote(symbol: str):
    """Financial Modeling Prep ticker quote

    Parameters
    ----------
    symbol : str
        Fundamental analysis ticker symbol
    """

    quote = stocks_model.get_quote(symbol)
    if quote.empty:
        console.print("[red]Data not found[/red]\n")
    else:
        print_rich_table(quote, headers=[""], title=f"{symbol} Quote", show_index=True)
