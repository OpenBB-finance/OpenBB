To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### etf.news(query: str, limit: int = 10, start_date: str = '2022-10-28', show_newest: bool = True, sources: str = '') -> List[Tuple[Any, Any]]

Get news for a given term. [Source: NewsAPI]

    Parameters
    ----------
    query : str
        term to search on the news articles
    start_date: str
        date to start searching articles from formatted YYYY-MM-DD
    show_newest: bool
        flag to show newest articles first
    sources: str
        sources to exclusively show news from (comma separated)

    Returns
    ----------
    tables : List[Tuple]
        List of tuples containing news df in first index and dict containing title of news df

## Getting charts 
### etf.news(query: str, limit: int = 3, start_date: str = '2022-10-28', show_newest: bool = True, sources: str = '', export: str = '', chart=True) -> None

Display news for a given term. [Source: NewsAPI]

    Parameters
    ----------
    query : str
        term to search on the news articles
    start_date: str
        date to start searching articles from formatted YYYY-MM-DD
    limit : int
        number of articles to display
    show_newest: bool
        flag to show newest articles first
    sources: str
        sources to exclusively show news from
    export : str
        Export dataframe data to csv,json,xlsx file
