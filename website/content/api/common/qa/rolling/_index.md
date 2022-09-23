To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### common.qa.rolling(data: pandas.core.frame.DataFrame, window: int = 14) -> Tuple[pandas.core.frame.DataFrame, pandas.core.frame.DataFrame]

Return rolling mean and standard deviation

    Parameters
    ----------
    data: pd.DataFrame
        Dataframe of target data
    window: int
        Length of rolling window

    Returns
    -------
    pd.DataFrame:
        Dataframe of rolling mean
    pd.DataFrame:
        Dataframe of rolling standard deviation

## Getting charts 
### common.qa.rolling(data: pandas.core.frame.DataFrame, target: str, symbol: str = '', window: int = 14, export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True) -> None

View mean std deviation

    Parameters
    ----------
    data: pd.DataFrame
        Dataframe
    target: str
        Column in data to look at
    symbol : str
        Stock ticker
    window : int
        Length of window
    export: str
        Format to export data
    external_axes: Optional[List[plt.Axes]], optional
        External axes (2 axes are expected in the list), by default None
