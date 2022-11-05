To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### common.ta.bbands(data: pandas.core.frame.DataFrame, window: int = 15, n_std: float = 2, mamode: str = 'ema') -> pandas.core.frame.DataFrame

Calculate Bollinger Bands

    Parameters
    ----------
    data : pd.DataFrame
        Dataframe of ohlc prices
    window : int
        Length of window to calculate BB
    n_std : float
        Number of standard deviations to show
    mamode : str
        Method of calculating average

    Returns
    -------
    df_ta: pd.DataFrame
        Dataframe of bollinger band data

## Getting charts 
### common.ta.bbands(data: pandas.core.frame.DataFrame, symbol: str = '', window: int = 15, n_std: float = 2, mamode: str = 'sma', export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True)

Show bollinger bands

    Parameters
    ----------
    data : pd.DataFrame
        Dataframe of ohlc prices
    symbol : str
        Ticker symbol
    window : int
        Length of window to calculate BB
    n_std : float
        Number of standard deviations to show
    mamode : str
        Method of calculating average
    export : str
        Format of export file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
