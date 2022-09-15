# alt.oss.search_repos

## Get underlying data 
###alt.oss.search_repos(sortby: str = 'stars', page: int = 1, categories: str = '') -> pandas.core.frame.DataFrame

Get repos sorted by stars or forks. Can be filtered by categories

    Parameters
    ----------
    sortby : str
            Sort repos by {stars, forks}
    categories : str
            Check for repo categories. If more than one separate with a comma: e.g., finance,investment. Default: None
    page : int
            Page number to get repos
    Returns
    -------
    pd.DataFrame with list of repos
