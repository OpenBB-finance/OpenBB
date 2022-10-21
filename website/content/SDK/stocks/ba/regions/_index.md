To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### stocks.ba.regions(symbol: str) -> pandas.core.frame.DataFrame

Get interest by region from google api [Source: google]

    Parameters
    ----------
    symbol: str
        Ticker symbol to look at

    Returns
    -------
    pd.DataFrame
        Dataframe of interest by region

## Getting charts 
### stocks.ba.regions(symbol: str, limit: int = 5, export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True)

Plot bars of regions based on stock's interest. [Source: Google]

    Parameters
    ----------
    symbol : str
        Ticker symbol
    limit: int
        Number of regions to show
    export: str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
