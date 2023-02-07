import logging

import pandas as pd

from openbb_terminal.decorators import check_api_key, log_start_end
from openbb_terminal.helper_funcs import print_rich_table
from openbb_terminal.rich_config import console
from openbb_terminal.stocks import stocks_model

logger = logging.getLogger(__name__)


def display_quote_yf(symbol: str) -> pd.DataFrame:
    """Display quote from YahooFinance"""
    quote_data = stocks_model.get_quote_yf(symbol)
    if quote_data is None:
        return pd.DataFrame()
    if quote_data.empty:
        return pd.DataFrame()
    print_rich_table(quote_data, title="Ticker Quote", show_index=True)
    return quote_data


@log_start_end(log=logger)
@check_api_key(["API_KEY_FINANCIALMODELINGPREP"])
def display_quote_fmp(symbol: str):
    """Financial Modeling Prep ticker quote

    Parameters
    ----------
    symbol : str
        Fundamental analysis ticker symbol
    """

    quote = stocks_model.get_quote_fmp(symbol)
    if quote.empty:
        console.print("[red]Data not found[/red]\n")
    else:
        print_rich_table(quote, headers=[""], title=f"{symbol} Quote", show_index=True)
