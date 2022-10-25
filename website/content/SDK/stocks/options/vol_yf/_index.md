To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### stocks.options.vol_yf(symbol: str, expiry: str) -> pandas.core.frame.DataFrame

Plot volume

    Parameters
    ----------
    symbol: str
        Ticker symbol
    expiry: str
        expiration date for options

## Getting charts 
### stocks.options.vol_yf(symbol: str, expiry: str, min_sp: float = -1, max_sp: float = -1, calls_only: bool = False, puts_only: bool = False, export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True)

Plot volume

    Parameters
    ----------
    symbol: str
        Ticker symbol
    expiry: str
        expiration date for options
    min_sp: float
        Min strike to consider
    max_sp: float
        Max strike to consider
    calls_only: bool
        Show calls only
    puts_only: bool
        Show puts only
    export: str
        Format to export file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
