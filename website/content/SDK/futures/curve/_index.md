To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### futures.curve(symbol: str = '')

Get curve futures [Source: Yahoo Finance]

    Parameters
    ----------
    symbol: str
        symbol to get forward curve

## Getting charts 
### futures.curve(symbol: str, raw: bool = False, export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True)

Display curve futures [Source: Yahoo Finance]

    Parameters
    ----------
    symbol: str
        Curve future symbol to display
    raw: bool
        Display futures timeseries in raw format
    export: str
        Type of format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
