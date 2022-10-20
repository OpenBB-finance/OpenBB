To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### stocks.ba.infer(symbol: str, limit: int = 100, start_date: Optional[str] = '', end_date: Optional[str] = '') -> pandas.core.frame.DataFrame

Load tweets from twitter API and analyzes using VADER

    Parameters
    ----------
    symbol: str
        Ticker symbol to search twitter for
    limit: int
        Number of tweets to analyze
    start_date: Optional[str]
        If given, the start time to get tweets from
    end_date: Optional[str]
        If given, the end time to get tweets from

    Returns
    -------
    df_tweet: pd.DataFrame
        Dataframe of tweets and sentiment

## Getting charts 
### stocks.ba.infer(symbol: str, limit: int = 100, export: str = '', chart=True)

Infer sentiment from past n tweets

    Parameters
    ----------
    symbol: str
        Stock ticker symbol
    limit: int
        Number of tweets to analyze
    export: str
        Format to export tweet dataframe
