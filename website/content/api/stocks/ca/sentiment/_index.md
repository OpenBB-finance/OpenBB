To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### stocks.ca.sentiment(symbols: List[str]) -> pandas.core.frame.DataFrame

Gets Sentiment analysis from several symbols provided by FinBrain's API

    Parameters
    ----------
    symbols : List[str]
        List of tickers to get sentiment
        Comparable companies can be accessed through
        finnhub_peers(), finviz_peers(), polygon_peers().

    Returns
    -------
    pd.DataFrame
        Contains sentiment analysis from several tickers

## Getting charts 
### stocks.ca.sentiment(similar: List[str], raw: bool = False, export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True)

Display sentiment for all ticker. [Source: FinBrain]

    Parameters
    ----------
    similar : List[str]
        Similar companies to compare income with.
        Comparable companies can be accessed through
        finviz_peers(), finnhub_peers() or polygon_peers().
    raw : bool, optional
        Output raw values, by default False
    export : str, optional
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
