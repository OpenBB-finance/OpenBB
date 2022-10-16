To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### stocks.ba.headlines(symbol: str) -> pandas.core.frame.DataFrame

Gets Sentiment analysis provided by FinBrain's API [Source: finbrain]

    Parameters
    ----------
    symbol : str
        Ticker symbol to get the sentiment analysis from

    Returns
    -------
    DataFrame()
        Empty if there was an issue with data retrieval

## Getting charts 
### stocks.ba.headlines(symbol: str, raw: bool = False, export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True)

Sentiment analysis from FinBrain

    Parameters
    ----------
    symbol: str
        Ticker symbol to get the sentiment analysis from
    raw: False
        Display raw table data
    export: str
        Format to export data
    external_axes: Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
