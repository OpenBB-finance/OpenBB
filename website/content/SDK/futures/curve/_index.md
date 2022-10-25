To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### futures.curve(ticker: str = '')

Get curve futures [Source: Yahoo Finance]

    Parameters
    ----------
    ticker: str
        Ticker to get forward curve

## Getting charts 
### futures.curve(ticker: str, raw: bool = False, export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True)

Display curve futures [Source: Yahoo Finance]

    Parameters
    ----------
    ticker: str
        Curve future ticker to display
    raw: bool
        Display futures timeseries in raw format
    export: str
        Type of format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
