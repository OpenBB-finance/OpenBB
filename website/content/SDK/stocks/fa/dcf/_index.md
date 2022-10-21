## Get underlying data 
### stocks.fa.dcf(symbol: str, limit: int = 5, quarterly: bool = False) -> pandas.core.frame.DataFrame

Get stocks dcf from FMP

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
        Dataframe of dcf data
