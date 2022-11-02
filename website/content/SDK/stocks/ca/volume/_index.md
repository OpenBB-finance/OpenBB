To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### stocks.ca.volume(similar: List[str], start_date: str = '2021-10-25') -> pandas.core.frame.DataFrame

Get stock volume. [Source: Yahoo Finance]

    Parameters
    ----------
    similar : List[str]
        List of similar tickers.
        Comparable companies can be accessed through
        finnhub_peers(), finviz_peers(), polygon_peers().
    start_date : str, optional
        Start date of comparison, by default 1 year ago

## Getting charts 
### stocks.ca.volume(similar: List[str], start_date: str = '2021-10-25', export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True)

Display stock volume. [Source: Yahoo Finance]

    Parameters
    ----------
    similar : List[str]
        List of similar tickers.
        Comparable companies can be accessed through
        finnhub_peers(), finviz_peers(), polygon_peers().
    start_date : str, optional
        Start date of comparison, by default 1 year ago
    export : str, optional
        Format to export historical prices, by default ""
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
