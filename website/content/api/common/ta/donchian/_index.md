To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### common.ta.donchian(high_prices: pandas.core.series.Series, low_prices: pandas.core.series.Series, upper_length: int = 20, lower_length: int = 20) -> pandas.core.frame.DataFrame

Calculate Donchian Channels

    Parameters
    ----------
    high_prices : pd.DataFrame
        High prices
    low_prices : pd.DataFrame
        Low prices
    upper_length : int
        Length of window to calculate upper channel
    lower_length : int
        Length of window to calculate lower channel

    Returns
    -------
    pd.DataFrame
        Dataframe of upper and lower channels

## Getting charts 
### common.ta.donchian(data: pandas.core.frame.DataFrame, symbol: str = '', upper_length: int = 20, lower_length: int = 20, export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True)

Show donchian channels

    Parameters
    ----------
    data : pd.DataFrame
        Dataframe of ohlc prices
    symbol : str
        Ticker symbol
    upper_length : int
        Length of window to calculate upper channel
    lower_length : int
        Length of window to calculate lower channel
    export : str
        Format of export file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
