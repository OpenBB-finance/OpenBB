To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### stocks.options.voi_yf(symbol: str, expiry: str) -> pandas.core.frame.DataFrame

Plot volume and open interest

    Parameters
    ----------
    symbol: str
        Stock ticker symbol
    expiry: str
        Option expiration

## Getting charts 
### stocks.options.voi_yf(symbol: str, expiry: str, min_sp: float = -1, max_sp: float = -1, min_vol: float = -1, export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True)

Plot volume and open interest

    Parameters
    ----------
    symbol: str
        Stock ticker symbol
    expiry: str
        Option expiration
    min_sp: float
        Min strike price
    max_sp: float
        Max strike price
    min_vol: float
        Min volume to consider
    export: str
        Format for exporting data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
