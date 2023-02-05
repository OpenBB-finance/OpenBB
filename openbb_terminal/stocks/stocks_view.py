import pandas as pd
from openbb_terminal.stocks import stocks_model
from openbb_terminal.helper_funcs import print_rich_table


def display_quote(symbol: str) -> pd.DataFrame:
    """Display quote from YahooFinance"""
    quote_data = stocks_model.load_quote(symbol)
    if quote_data is None:
        return pd.DataFrame()
    if quote_data.empty:
        return pd.DataFrame()
    print_rich_table(quote_data, title="Ticker Quote", show_index=True)
    return quote_data
