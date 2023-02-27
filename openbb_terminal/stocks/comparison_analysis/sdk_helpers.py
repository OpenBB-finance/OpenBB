"""CA SDK Helpers."""
__docformat__ = "numpy"

from typing import List

from openbb_terminal.stocks.comparison_analysis import (
    finnhub_model,
    finviz_compare_model,
    polygon_model,
    yahoo_finance_model,
)


def get_similar(symbol: str, source="Finviz") -> List[str]:
    """Find similar tickers to a given symbol.

    Parameters
    ----------
    symbol : str
        Symbol to find similar tickers to.
    source : str, optional
        Source to get data for, by default "Finviz".  Can be "Finviz", "Polygon", "Finnhub", or "TSNE"

    Returns
    -------
    List[str]
       List of similar tickers.

    Examples
    --------
    To get similar tickers to AAPL from Finviz:
    >>> from openbb_terminal.sdk import openbb
    >>> similar_tickers = openbb.stocks.ca.similar("AAPL")

    To use our custom TSNE model for similar tickers in the SP500:
    >>> similar_tickers = openbb.stocks.ca.similar("AAPL", source="TSNE")
    """
    if source.lower() == "finviz":
        return finviz_compare_model.get_similar_companies(symbol)

    if source.lower() == "polygon":
        return polygon_model.get_similar_companies(symbol)

    if source.lower() == "finnhub":
        return finnhub_model.get_similar_companies(symbol)

    if source.lower() == "tsne":
        return yahoo_finance_model.get_sp500_comps_tsne(symbol).index.to_list()[:10]

    return []
