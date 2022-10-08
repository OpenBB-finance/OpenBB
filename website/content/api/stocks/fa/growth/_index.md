## Get underlying data 
### stocks.fa.growth(symbol: str, limit: int = 5, quarterly: bool = False) -> pandas.core.frame.DataFrame

Get financial statement growth

    Parameters
    ----------
    symbol : str
        Stock ticker symbol
    limit : int
        Number to get
    quarterly : bool, optional
        Flag to get quarterly data, by default False

    Returns
    -------
    pd.DataFrame
        Dataframe of financial statement growth
