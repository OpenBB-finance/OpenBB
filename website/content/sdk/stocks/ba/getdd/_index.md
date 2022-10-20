## Get underlying data 
### stocks.ba.getdd(symbol: str, limit: int = 5, n_days: int = 3, show_all_flairs: bool = False) -> pandas.core.frame.DataFrame

Gets due diligence posts from list of subreddits [Source: reddit]

    Parameters
    ----------
    symbol: str
        Stock ticker
    limit: int
        Number of posts to get
    n_days: int
        Number of days back to get posts
    show_all_flairs: bool
        Search through all flairs (apart from Yolo and Meme)

    Returns
    -------
    pd.DataFrame
        Dataframe of submissions
