## Get underlying data 
### stocks.ba.spac(limit: int = 5) -> Tuple[pandas.core.frame.DataFrame, dict, int]

Get posts containing SPAC from top subreddits [Source: reddit]

    Parameters
    ----------
    limit : int, optional
        Number of posts to get for each subreddit, by default 5

    Returns
    -------
    pd.DataFrame :
        Dataframe of reddit submissions
    dict :
        Dictionary of tickers and counts
    int :
        Number of posts found.
