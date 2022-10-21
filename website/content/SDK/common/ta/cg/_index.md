To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### common.ta.cg(values: pandas.core.series.Series, window: int) -> pandas.core.frame.DataFrame

Center of gravity

    Parameters
    ----------
    values: pd.DataFrame
        Data to use with close being titled values
    window: int
        Length for indicator window
    Returns
    ----------
    pd.DataFrame
        Dataframe of technical indicator

## Getting charts 
### common.ta.cg(data: pandas.core.series.Series, window: int = 14, symbol: str = '', export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True)

Display center of gravity Indicator

    Parameters
    ----------
    data : pd.Series
        Series of values
    window : int
        Length of window
    symbol : str
        Stock ticker
    export : str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (2 axes are expected in the list), by default None
