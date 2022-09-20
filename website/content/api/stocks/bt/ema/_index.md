# stocks.bt.ema

To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
###stocks.bt.ema(symbol: str, data: pandas.core.frame.DataFrame, ema_length: int = 20, spy_bt: bool = True, no_bench: bool = False) -> bt.backtest.Result

Perform backtest for simple EMA strategy.  Buys when price>EMA(l)

    Parameters
    ----------
    symbol: str
        Stock ticker
    data: pd.DataFrame
        Dataframe of prices
    ema_length: int
        Length of ema window
    spy_bt: bool
        Boolean to add spy comparison
    no_bench: bool
        Boolean to not show buy and hold comparison

    Returns
    -------
    bt.backtest.Result
        Backtest results

## Getting charts 
###stocks.bt.ema(symbol: str, data: pandas.core.frame.DataFrame, ema_length: int = 20, spy_bt: bool = True, no_bench: bool = False, export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True)

Strategy where stock is bought when Price > EMA(l)

    Parameters
    ----------
    symbol : str
        Stock ticker
    data : pd.Dataframe
        Dataframe of prices
    ema_length : int
        Length of ema window
    spy_bt : bool
        Boolean to add spy comparison
    no_bench : bool
        Boolean to not show buy and hold comparison
    export : bool
        Format to export backtest results
    external_axes : Optional[List[plt.Axes]], optional
        External axes (3 axes are expected in the list), by default None
