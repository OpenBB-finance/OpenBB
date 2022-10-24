To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### stocks.ta.view(symbol: str) -> bytes

Get finviz image for given ticker

    Parameters
    ----------
    symbol: str
        Ticker symbol

    Returns
    -------
    bytes
        Image in byte format

## Getting charts 
### stocks.ta.view(symbol: str, external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True)

View finviz image for ticker

    Parameters
    ----------
    symbol: str
        Stock ticker symbol
    external_axes: Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
