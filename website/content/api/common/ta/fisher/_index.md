To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### common.ta.fisher(high_vals: pandas.core.series.Series, low_vals: pandas.core.series.Series, window: int = 14) -> pandas.core.frame.DataFrame

Fisher Transform

    Parameters
    ----------
    high_vals: pd.Series
        High values
    low_vals: pd.Series
        Low values
    window: int
        Length for indicator window
    Returns
    ----------
    df_ta: pd.DataFrame
        Dataframe of technical indicator

## Getting charts 
### common.ta.fisher(data: pandas.core.frame.DataFrame, window: int = 14, symbol: str = '', export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True)

Display Fisher Indicator

    Parameters
    ----------
    data : pd.DataFrame
        Dataframe of OHLC prices
    window : int
        Length of window
    symbol : str
        Ticker string
    export : str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (3 axes are expected in the list), by default None
