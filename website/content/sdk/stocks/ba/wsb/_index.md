## Get underlying data 
### stocks.ba.wsb(limit: int = 10, new: bool = False) -> pandas.core.frame.DataFrame

Get wsb posts [Source: reddit]

    Parameters
    ----------
    limit : int, optional
        Number of posts to get, by default 10
    new : bool, optional
        Flag to sort by new instead of hot, by default False

    Returns
    -------
    pd.DataFrame
        Dataframe of reddit submissions
