To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### common.ta.rsi(data: pandas.core.series.Series, window: int = 14, scalar: float = 100, drift: int = 1) -> pandas.core.frame.DataFrame

Relative strength index

    Parameters
    ----------
    data: pd.Series
        Dataframe of prices
    window: int
        Length of window
    scalar: float
        Scalar variable
    drift: int
        Drift variable

    Returns
    ----------
    pd.DataFrame
        Dataframe of technical indicator

## Getting charts 
### common.ta.rsi(data: pandas.core.series.Series, window: int = 14, scalar: float = 100.0, drift: int = 1, symbol: str = '', export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True)

Display RSI Indicator

    Parameters
    ----------
    data : pd.Series
        Values to input
    window : int
        Length of window
    scalar : float
        Scalar variable
    drift : int
        Drift variable
    symbol : str
        Stock ticker
    export : str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (2 axes are expected in the list), by default None
