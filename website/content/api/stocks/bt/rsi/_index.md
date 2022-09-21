# stocks.bt.rsi

To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
###stocks.bt.rsi(symbol: str, data: pandas.core.frame.DataFrame, periods: int = 14, low_rsi: int = 30, high_rsi: int = 70, spy_bt: bool = True, no_bench: bool = False, shortable: bool = True) -> bt.backtest.Result

Perform backtest for simple EMA strategy. Buys when price>EMA(l)

    Parameters
    ----------
    symbol : str
        Stock ticker
    data : pd.DataFrame
        Dataframe of prices
    periods : int
        Number of periods for RSI calculation
    low_rsi : int
        Low RSI value to buy
    high_rsi : int
        High RSI value to sell
    spy_bt : bool
        Boolean to add spy comparison
    no_bench : bool
        Boolean to not show buy and hold comparison
    shortable : bool
        Flag to disable the ability to short sell

    Returns
    -------
    Result
        Backtest results

## Getting charts 
###stocks.bt.rsi(symbol: str, data: pandas.core.frame.DataFrame, periods: int = 14, low_rsi: int = 30, high_rsi: int = 70, spy_bt: bool = True, no_bench: bool = False, shortable: bool = True, export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True)

Strategy that buys when the stock is less than a threshold and shorts when it exceeds a threshold.

    Parameters
    ----------
    symbol : str
        Stock ticker
    data : pd.Dataframe
        Dataframe of prices
    periods : int
        Number of periods for RSI calculation
    low_rsi : int
        Low RSI value to buy
    high_rsi : int
        High RSI value to sell
    spy_bt : bool
        Boolean to add spy comparison
    no_bench : bool
        Boolean to not show buy and hold comparison
    shortable : bool
        Boolean to allow for selling of the stock at cross
    export : str
        Format to export backtest results
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
