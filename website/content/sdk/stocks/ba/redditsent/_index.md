To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### stocks.ba.redditsent(symbol: str, limit: int = 100, sortby: str = 'relevance', time_frame: str = 'week', full_search: bool = True, subreddits: str = 'all') -> Tuple[pandas.core.frame.DataFrame, list, float]

Finds posts related to a specific search term in Reddit

    Parameters
    ----------
    symbol: str
        Ticker symbol to search for
    limit: int
        Number of posts to get per subreddit
    sortby: str
        Search type
        Possibilities: "relevance", "hot", "top", "new", or "comments"
    time_frame: str
        Relative time of post
        Possibilities: "hour", "day", "week", "month", "year", "all"
    full_search: bool
        Enable comprehensive search for ticker
    subreddits: str
        Comma-separated list of subreddits

    Returns
    -------
    tuple[pd.DataFrame, list, float]:
        Dataframe of submissions related to the search term,
        List of polarity scores,
        Average polarity score

## Getting charts 
### stocks.ba.redditsent(symbol: str, sortby: str = 'relevance', limit: int = 100, graphic: bool = False, time_frame: str = 'week', full_search: bool = True, subreddits: str = 'all', display: bool = False, export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True)

Determine Reddit sentiment about a search term
    Parameters
    ----------
    symbol: str
        The ticker symbol being search for in Reddit
    sortby: str
        Type of search
    limit: str
        Number of posts to get at most
    graphic: bool
        Displays box and whisker plot
    time_frame: str
        Time frame for search
    full_search: bool
        Enable comprehensive search for ticker
    subreddits: str
        Comma-separated list of subreddits
    display: bool
        Enable printing of raw sentiment values for each post
    export: str
        Format to export data
    external_axes: Optional[List[plt.Axes]]
        If supplied, expect 1 external axis
