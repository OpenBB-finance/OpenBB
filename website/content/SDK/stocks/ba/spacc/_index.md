## Get underlying data
### stocks.ba.spacc(limit: int = 10, popular: bool = False) -> Tuple[pandas.core.frame.DataFrame, dict]

Get top tickers from r/SPACs [Source: reddit]

    Parameters
    ----------
    limit : int
        Number of posts to look at
    popular : bool
        Search by hot instead of new

    Returns
    -------
    pd.DataFrame:
        Dataframe of reddit submission
    dict:
        Dictionary of tickers and number of mentions
