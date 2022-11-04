To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### common.ta.aroon(data: pandas.core.frame.DataFrame, window: int = 25, scalar: int = 100) -> pandas.core.frame.DataFrame

Aroon technical indicator

    Parameters
    ----------
    data : pd.DataFrame
        Dataframe with OHLC price data
    window : int
        Length of window
    scalar : int
        Scalar variable

    Returns
    -------
    pd.DataFrame
        DataFrame with aroon indicator

## Getting charts 
### common.ta.aroon(data: pandas.core.frame.DataFrame, window: int = 25, scalar: int = 100, symbol: str = '', export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True)

Plot Aroon indicator

    Parameters
    ----------
    data: pd.DataFrame
        Dataframe with OHLC price data
    window: int
        Length of window
    symbol: str
        Ticker
    scalar: int
        Scalar variable
    export: str
        Format to export data
    external_axes: Optional[List[plt.Axes]], optional
        External axes (3 axes are expected in the list), by default None
