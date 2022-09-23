To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### stocks.ba.watchlist(limit: int = 5) -> Tuple[List[praw.models.reddit.submission.Submission], dict, int]

Get reddit users watchlists [Source: reddit]

    Parameters
    ----------
    limit : int
        Number of posts to look through

    Returns
    -------
    list[praw.models.reddit.submission.Submission]:
        List of reddit submissions
    dict:
        Dictionary of tickers and counts
    int
        Count of how many posts were analyzed

## Getting charts 
### stocks.ba.watchlist(limit: int = 5, chart=True)

Print other users watchlist. [Source: Reddit]

    Parameters
    ----------
    limit: int
        Maximum number of submissions to look at
