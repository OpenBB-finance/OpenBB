"""AlphaVantage Forex View"""
__docformat__ = "numpy"

import pandas as pd
from tabulate import tabulate

from gamestonk_terminal.forex import av_model
from gamestonk_terminal import feature_flags as gtff


def display_quote(to_symbol: str, from_symbol: str):
    """Display current forex pair exchange rate

    Parameters
    ----------
    to_symbol : str
        To symbol
    from_symbol : str
        From forex symbol
    """
    quote = av_model.get_quote(to_symbol, from_symbol)

    if not quote:
        print("Quote not pulled from AlphaVantage.  Check API key.")
        return

    df = pd.DataFrame.from_dict(quote)
    df.index = df.index.to_series().apply(lambda x: x[3:]).values
    df = df.iloc[[0, 2, 5, 4, 7, 8]]
    if gtff.USE_TABULATE_DF:
        print(tabulate(df, tablefmt="fancy_grid"))
    else:
        print(df.to_string())
