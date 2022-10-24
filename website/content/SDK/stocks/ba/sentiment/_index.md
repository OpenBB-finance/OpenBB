To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### stocks.ba.sentiment(symbol: str, n_tweets: int = 15, n_days_past: int = 2) -> pandas.core.frame.DataFrame

Get sentiments from symbol

    Parameters
    ----------
    symbol: str
        Stock ticker symbol to get sentiment for
    n_tweets: int
        Number of tweets to get per hour
    n_days_past: int
        Number of days to extract tweets for

## Getting charts 
### stocks.ba.sentiment(symbol: str, n_tweets: int = 15, n_days_past: int = 2, compare: bool = False, export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True)

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
