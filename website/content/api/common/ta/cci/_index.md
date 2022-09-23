To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### common.ta.cci(data: pandas.core.frame.DataFrame, window: int = 14, scalar: float = 0.0015) -> pandas.core.frame.DataFrame

Commodity channel index

    Parameters
    ----------
    high_vals: pd.Series
        High values
    low_values: pd.Series
        Low values
    close-values: pd.Series
        Close values
    window: int
        Length of window
    scalar: float
        Scalar variable

    Returns
    ----------
    pd.DataFrame
        Dataframe of technical indicator

## Getting charts 
### common.ta.cci(data: pandas.core.frame.DataFrame, window: int = 14, scalar: float = 0.0015, symbol: str = '', export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True)

Display CCI Indicator

    Parameters
    ----------

    data : pd.DataFrame
        Dataframe of OHLC
    window : int
        Length of window
    scalar : float
        Scalar variable
    symbol : str
        Stock ticker
    export : str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (2 axes are expected in the list), by default None
