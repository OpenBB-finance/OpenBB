To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### common.ta.kc(high_prices: pandas.core.series.Series, low_prices: pandas.core.series.Series, close_prices: pandas.core.series.Series, window: int = 20, scalar: float = 2, mamode: str = 'ema', offset: int = 0) -> pandas.core.frame.DataFrame

Keltner Channels

    Parameters
    ----------
    high_prices : pd.DataFrame
        High prices
    low_prices : pd.DataFrame
        Low prices
    close_prices : pd.DataFrame
        Close prices
    window : int
        Length of window
    scalar: float
        Scalar value
    mamode: str
        Type of filter
    offset : int
        Offset value

    Returns
    -------
    pd.DataFrame
        Dataframe of rolling kc

## Getting charts 
### common.ta.kc(data: pandas.core.frame.DataFrame, window: int = 20, scalar: float = 2, mamode: str = 'ema', offset: int = 0, symbol: str = '', export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True)

View Keltner Channels Indicator

    Parameters
    ----------

    data: pd.DataFrame
        Dataframe of ohlc prices
    window: int
        Length of window
    scalar: float
        Scalar value
    mamode: str
        Type of filter
    offset: int
        Offset value
    symbol: str
        Ticker symbol
    export: str
        Format to export data
    external_axes: Optional[List[plt.Axes]], optional
        External axes (2 axes are expected in the list), by default None
