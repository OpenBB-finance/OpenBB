## Get underlying data 
### stocks.process_candle(data: pandas.core.frame.DataFrame) -> pandas.core.frame.DataFrame

Process DataFrame into candle style plot.

    Parameters
    ----------
    data : DataFrame
        Stock dataframe.

    Returns
    -------
    DataFrame
        A Panda's data frame with columns Open, High, Low, Close, Adj Close, Volume,
        date_id, OC-High, OC-Low.
