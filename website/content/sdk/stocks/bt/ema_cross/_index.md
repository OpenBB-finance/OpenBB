# stocks.bt.ema_cross

To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
###stocks.bt.ema_cross(symbol: str, data: pandas.core.frame.DataFrame, short_length: int = 20, long_length: int = 50, spy_bt: bool = True, no_bench: bool = False, shortable: bool = True) -> bt.backtest.Result

Perform backtest for simple EMA strategy. Buys when price>EMA(l)

    Parameters
    ----------
    symbol : str
        Stock ticker
    data : pd.DataFrame
        Dataframe of prices
    short_length : int
        Length of short ema window
    long_length : int
        Length of long ema window
    spy_bt : bool
        Boolean to add spy comparison
    no_bench : bool
        Boolean to not show buy and hold comparison
    shortable : bool
        Boolean to allow for selling of the stock at cross

    Returns
    -------
    Result
        Backtest results

## Getting charts 
###stocks.bt.ema_cross(symbol: str, data: pandas.core.frame.DataFrame, short_ema: int = 20, long_ema: int = 50, spy_bt: bool = True, no_bench: bool = False, shortable: bool = True, export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True)

Strategy where we go long/short when EMA(short) is greater than/less than EMA(short)

    Parameters
    ----------
    symbol : str
        Stock ticker
    data : pd.Dataframe
        Dataframe of prices
    short_ema : int
        Length of short ema window
    long_ema : int
        Length of long ema window
    spy_bt : bool
        Boolean to add spy comparison
    no_bench : bool
        Boolean to not show buy and hold comparison
    shortable : bool
        Boolean to allow for selling of the stock at cross
    export : str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
