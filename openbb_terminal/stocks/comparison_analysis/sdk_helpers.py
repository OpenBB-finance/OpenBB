"""CA SDK Helpers."""

__docformat__ = "numpy"

from typing import List

from openbb_terminal.stocks.comparison_analysis import (
    finnhub_model,
    polygon_model,
)


def get_similar(symbol: str, source="polygon") -> List[str]:
    """Find similar tickers to a given symbol.

    Parameters
    ----------
    symbol : str
        Symbol to find similar tickers to.
    source : str, optional
        Source to get data for, by default "polygon".  Can be "Polygon", "Finnhub"

    Returns
    -------
    List[str]
       List of similar tickers.

    Examples
    --------
    To get similar tickers to AAPL from polygon:
    >>> from openbb_terminal.sdk import openbb
    >>> similar_tickers = openbb.stocks.ca.similar("AAPL")

    """
    if source.lower() == "polygon":
        return polygon_model.get_similar_companies(symbol)

    if source.lower() == "finnhub":
        return finnhub_model.get_similar_companies(symbol)

    return []
