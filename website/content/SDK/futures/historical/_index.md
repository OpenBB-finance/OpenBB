To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### futures.historical(tickers: List[str], expiry: str = '') -> Dict

Get historical futures [Source: Yahoo Finance]

    Parameters
    ----------
    tickers: List[str]
        List of future timeseries tickers to display
    expiry: str
        Future expiry date with format YYYY-MM

    Returns
    ----------
    Dict
        Dictionary with sector weightings allocation

## Getting charts 
### futures.historical(tickers: List[str], expiry: str = '', start_date: str = '2019-11-04', raw: bool = False, export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True)

Display historical futures [Source: Yahoo Finance]

    Parameters
    ----------
    tickers: List[str]
        List of future timeseries tickers to display
    expiry: str
        Future expiry date with format YYYY-MM
    start_date : str
        Initial date like string (e.g., 2021-10-01)
    raw: bool
        Display futures timeseries in raw format
    export: str
        Type of format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
