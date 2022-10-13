## Get underlying data 
### forecast.ema(dataset: pandas.core.frame.DataFrame, target_column: str = 'close', period: int = 10) -> pandas.core.frame.DataFrame

A moving average provides an indication of the trend of the price movement
    by cut down the amount of "noise" on a price chart.

    Parameters
    ----------
    dataset : pd.DataFrame
        The dataset you wish to clean
    target_column : str
        The column you wish to add the EMA to
    period : int
        Time Span

    Returns
    -------
    pd.DataFrame:
        Dataframe with added EMA column
