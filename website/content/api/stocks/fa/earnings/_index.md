## Get underlying data 
### stocks.fa.earnings(symbol: str, quarterly: bool = False) -> pandas.core.frame.DataFrame

Get earnings calendar for ticker

    Parameters
    ----------
    symbol : str
        Stock ticker symbol
    quarterly : bool, optional
        Flag to get quarterly and not annual, by default False

    Returns
    -------
    pd.DataFrame
        Dataframe of earnings
