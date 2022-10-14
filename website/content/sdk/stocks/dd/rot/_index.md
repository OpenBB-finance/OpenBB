To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### stocks.dd.rot(symbol: str) -> pandas.core.frame.DataFrame

Get rating over time data. [Source: Finnhub]

    Parameters
    ----------
    symbol : str
        Ticker symbol to get ratings from

    Returns
    -------
    pd.DataFrame
        Get dataframe with ratings

## Getting charts 
### stocks.dd.rot(symbol: str, limit: int = 10, raw: bool = False, export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True)

Rating over time (monthly). [Source: Finnhub]

    Parameters
    ----------
    ticker : str
        Ticker to get ratings from
    limit : int
        Number of last months ratings to show
    raw: bool
        Display raw data only
    export: str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]]
        External axes (1 axis is expected in the list), by default None
