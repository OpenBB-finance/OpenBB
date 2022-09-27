## Get underlying data 
### economy.fred_ids(search_query: str, limit: int = -1) -> pandas.core.frame.DataFrame

Get Series IDs. [Source: FRED]
    Parameters
    ----------
    search_query : str
        Text query to search on fred series notes database
    limit : int
        Maximum number of series IDs to output
    Returns
    ----------
    pd.Dataframe
        Dataframe with series IDs and titles
