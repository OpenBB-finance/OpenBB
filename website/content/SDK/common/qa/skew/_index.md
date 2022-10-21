To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### common.qa.skew(data: pandas.core.frame.DataFrame, window: int = 14) -> pandas.core.frame.DataFrame

Skewness Indicator

    Parameters
    ----------
    data: pd.DataFrame
        Dataframe of targeted data
    window : int
        Length of window

    Returns
    -------
    data_skew : pd.DataFrame
        Dataframe of rolling skew

## Getting charts 
### common.qa.skew(symbol: str, data: pandas.core.frame.DataFrame, target: str, window: int = 14, export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True) -> None

View rolling skew

    Parameters
    ----------
    symbol: str
        Stock ticker
    data: pd.DataFrame
        Dataframe
    target: str
        Column in data to look at
    window: int
        Length of window
    export: str
        Format to export data
    external_axes: Optional[List[plt.Axes]], optional
        External axes (2 axes are expected in the list), by default None
