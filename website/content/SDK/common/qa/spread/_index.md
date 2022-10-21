To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### common.qa.spread(data: pandas.core.frame.DataFrame, window: int = 14) -> Tuple[pandas.core.frame.DataFrame, pandas.core.frame.DataFrame]

Standard Deviation and Variance

    Parameters
    ----------
    data: pd.DataFrame
        DataFrame of targeted data
    window: int
        Length of window

    Returns
    -------
    df_sd: pd.DataFrame
        Dataframe of rolling standard deviation
    df_var: pd.DataFrame
        Dataframe of rolling standard deviation

## Getting charts 
### common.qa.spread(data: pandas.core.frame.DataFrame, target: str, symbol: str = '', window: int = 14, export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True)

View rolling spread

    Parameters
    ----------
    data: pd.DataFrame
        Dataframe
    target: str
        Column in data to look at
    target: str
        Column in data to look at
    symbol : str
        Stock ticker
    window : int
        Length of window
    export: str
        Format to export data
    external_axes: Optional[List[plt.Axes]], optional
        External axes (3 axes are expected in the list), by default None
