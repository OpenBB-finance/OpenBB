# alt.oss.top_repos

To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
###alt.oss.top_repos(sortby: str, top: int, categories: str) -> pandas.core.frame.DataFrame

Get repos sorted by stars or forks. Can be filtered by categories

    Parameters
    ----------
    sortby : str
            Sort repos by {stars, forks}
    categories : str
            Check for repo categories. If more than one separate with a comma: e.g., finance,investment. Default: None
    top : int
            Number of repos to search for
    Returns
    -------
    pd.DataFrame with list of repos

## Getting charts 
###alt.oss.top_repos(sortby: str, categories: str, limit: int, export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True) -> None

Display repo summary [Source: https://api.github.com]

    Parameters
    ----------
    sortby : str
            Sort repos by {stars, forks}
    categories : str
            Check for repo categories. If more than one separate with a comma: e.g., finance,investment. Default: None
    limit : int
    Number of repos to look at
    export : str
    Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
    External axes (1 axis is expected in the list), by default None
