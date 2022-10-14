To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### stocks.ba.mentions(symbol: str) -> pandas.core.frame.DataFrame

Get interest over time from google api [Source: google]

    Parameters
    ----------
    symbol: str
        Stock ticker symbol

    Returns
    -------
    pd.DataFrame
        Dataframe of interest over time

## Getting charts 
### stocks.ba.mentions(symbol: str, start_date: str = '', export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True)

Plot weekly bars of stock's interest over time. other users watchlist. [Source: Google]

    Parameters
    ----------
    symbol : str
        Ticker symbol
    start_date : str
        Start date as YYYY-MM-DD string
    export: str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
