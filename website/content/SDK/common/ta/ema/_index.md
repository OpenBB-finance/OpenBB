## Get underlying data 
### common.ta.ema(data: pandas.core.series.Series, length: int = 50, offset: int = 0) -> pandas.core.frame.DataFrame

Gets exponential moving average (EMA) for stock

    Parameters
    ----------
    data: pd.Series
        Dataframe of dates and prices
    length: int
        Length of EMA window
    offset: int
        Length of offset

    Returns
    ----------
    pd.DataFrame
        Dataframe containing prices and EMA
