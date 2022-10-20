To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### stocks.ba.trend(start_date: datetime.datetime = datetime.datetime(2022, 10, 20, 14, 0, 53, 374094), hour: int = 0, number: int = 10) -> pandas.core.frame.DataFrame

Get sentiment data on the most talked about tickers
    within the last hour

    Source: [Sentiment Investor]

    Parameters
    ----------
    start_date: datetime
        Datetime object (e.g. datetime(2021, 12, 21)
    hour: int
        Hour of the day in 24-hour notation (e.g. 14)
    number : int
        Number of results returned by API call
        Maximum 250 per api call

    Returns
    -------
    pd.DataFrame
        Dataframe of trending data

## Getting charts 
### stocks.ba.trend(start_date: datetime.datetime = datetime.datetime(2022, 10, 20, 14, 0, 53, 374320, chart=True), hour: int = 0, number: int = 10, limit: int = 10, export: str = '')

Display most talked about tickers within
    the last hour together with their sentiment data.

    Parameters
    ----------
    start_date: datetime
        Datetime object (e.g. datetime(2021, 12, 21)
    hour: int
        Hour of the day in 24-hour notation (e.g. 14)
    number : int
        Number of results returned by API call
        Maximum 250 per api call
    limit: int
        Number of results display on the terminal
        Default: 10
    export: str
        Format to export data
