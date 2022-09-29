## Get underlying data 
### economy.fred_notes(search_query: str, limit: int = -1) -> pandas.core.frame.DataFrame

Get series notes. [Source: FRED]
    Parameters
    ----------
    search_query : str
        Text query to search on fred series notes database
    limit : int
        Maximum number of series notes to display
    Returns
    ----------
    pd.DataFrame
        DataFrame of matched series
