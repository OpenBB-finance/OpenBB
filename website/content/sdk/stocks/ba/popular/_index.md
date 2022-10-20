To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### stocks.ba.popular(limit: int = 10, post_limit: int = 50, subreddits: str = '') -> pandas.core.frame.DataFrame

Get popular tickers from list of subreddits [Source: reddit]

    Parameters
    ----------
    limit : int
        Number of top tickers to get
    post_limit : int
        How many posts to analyze in each subreddit
    subreddits : str, optional
        String of comma separated subreddits.

    Returns
    -------
    pd.DataFrame
        DataFrame of top tickers from supplied subreddits

## Getting charts 
### stocks.ba.popular(limit: int = 10, post_limit: int = 50, subreddits: str = '', export: str = '', chart=True)

Print latest popular tickers. [Source: Reddit]

    Parameters
    ----------
    limit : int
        Number of top tickers to get
    post_limit : int
        How many posts to analyze in each subreddit
    subreddits : str, optional
        String of comma separated subreddits.
    export : str
        Format to export dataframe
