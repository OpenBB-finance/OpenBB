## Get underlying data 
### stocks.fa.fmp_ratios(symbol: str, limit: int = 5, quarterly: bool = False) -> pandas.core.frame.DataFrame

Get key ratios

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
        Dataframe of key ratios
