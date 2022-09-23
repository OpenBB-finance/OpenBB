## Get underlying data 
### stocks.ba.rise(symbol: str, limit: int = 10) -> pandas.core.frame.DataFrame

Get top rising related queries with this stock's query [Source: google]

    Parameters
    ----------
    symbol: str
        Stock ticker symbol
    limit: int
        Number of queries to show

    Returns
    -------
    pd.DataFrame
        Dataframe containing rising related queries
