## Get underlying data 
### common.ta.sma(data: pandas.core.series.Series, length: int = 50, offset: int = 0) -> pandas.core.frame.DataFrame

Gets simple moving average (EMA) for stock

     Parameters
     ----------
     data: pd.Series
         Dataframe of dates and prices
     length: int
         Length of SMA window
     offset: int
         Length of offset

     Returns
     ----------
    pd.DataFrame
         Dataframe containing prices and SMA
