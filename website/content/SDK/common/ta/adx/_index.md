To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### common.ta.adx(high_values: pandas.core.series.Series, low_values: pandas.core.series.Series, close_values: pandas.core.series.Series, window: int = 14, scalar: int = 100, drift: int = 1)

ADX technical indicator

    Parameters
    ----------
    high_values: pd.Series
        High prices
    low_values: pd.Series
        Low prices
    close_values: pd.Series
        close prices
    window: int
        Length of window
    scalar: int
        Scalar variable
    drift: int
        Drift variable

    Returns
    -------
    pd.DataFrame
        DataFrame with adx indicator

## Getting charts 
### common.ta.adx(data: pandas.core.frame.DataFrame, window: int = 14, scalar: int = 100, drift: int = 1, symbol: str = '', export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True)

Plot ADX indicator

    Parameters
    ----------
    data : pd.DataFrame
        Dataframe with OHLC price data
    window : int
        Length of window
    scalar : int
        Scalar variable
    drift : int
        Drift variable
    symbol : str
        Ticker
    export : str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (2 axes are expected in the list), by default None
