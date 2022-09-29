## Get underlying data 
### economy.events(country: str = 'all', importance: str = '', category: str = '', start_date: str = '', end_date: str = '', limit=100) -> Tuple[pandas.core.frame.DataFrame, str]

Get economic calendar [Source: Investing.com]

    Parameters
    ----------
    country: str
        Country selected. List of available countries is accessible through get_events_countries().
    importance: str
        Importance selected from high, medium, low or all
    category: str
        Event category. List of available categories is accessible through get_events_categories().
    start_date: datetime.date
        First date to get events.
    end_date: datetime.date
        Last date to get events.

    Returns
    -------
    Tuple[pd.DataFrame, str]
        Economic calendar Dataframe and detail string about country/time zone.
