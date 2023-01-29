"""ETF Helper module."""
__docformat__ = "numpy"

import yfinance as yf


def get_quote_type(symbol: str) -> str:
    """Get the quote type of the symbol.

    Parameters
    ----------
    symbol : str
        Ticker to check.

    Returns
    -------
    str
        Returns the quote type of the symbol.
    """
    try:
        quote_type = yf.Ticker(symbol).info["quoteType"]
        return quote_type
    except TypeError:
        return "N/A"
