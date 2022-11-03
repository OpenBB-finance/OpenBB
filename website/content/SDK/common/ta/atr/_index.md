To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### common.ta.atr(data: pandas.core.frame.DataFrame, window: int = 14, mamode: str = 'ema', offset: int = 0) -> pandas.core.frame.DataFrame

Average True Range

    Parameters
    ----------
    data : pd.DataFrame
        Dataframe of ohlc prices
    window : int
        Length of window
    mamode: str
        Type of filter
    offset : int
        Offset value

    Returns
    -------
    pd.DataFrame
        Dataframe of atr

## Getting charts 
### common.ta.atr(data: pandas.core.frame.DataFrame, symbol: str = '', window: int = 14, mamode: str = 'sma', offset: int = 0, export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True)

Show ATR

    Parameters
    ----------
    data : pd.DataFrame
        Dataframe of ohlc prices
    symbol : str
        Ticker symbol
    window : int
        Length of window to calculate upper channel
    export : str
        Format of export file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
