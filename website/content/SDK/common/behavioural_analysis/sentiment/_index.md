# common.behavioural_analysis.sentiment

To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
###common.behavioural_analysis.sentiment(post_data: List[str]) -> float

Find the sentiment of a post and related comments

    Parameters
    ----------
    post_data: List[str]
        A post and its comments in string form

    Returns
    -------
    float
        A number in the range [-1, 1] representing sentiment

## Getting charts 
###common.behavioural_analysis.sentiment(symbol: str, n_tweets: int = 15, n_days_past: int = 2, compare: bool = False, export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True)

Plot sentiments from symbol

    Parameters
    ----------
    symbol: str
        Stock ticker symbol to get sentiment for
    n_tweets: int
        Number of tweets to get per hour
    n_days_past: int
        Number of days to extract tweets for
    compare: bool
        Show corresponding change in stock price
    export: str
        Format to export tweet dataframe
    external_axes: Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
