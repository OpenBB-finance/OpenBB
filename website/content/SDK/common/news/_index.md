## Get underlying data 
### common.news(term: str = '', sources: str = '', sort: str = 'published') -> pandas.core.frame.DataFrame

Get news for a given term and source. [Source: Feedparser]

    Parameters
    ----------
    term : str
        term to search on the news articles
    sources: str
        sources to exclusively show news from (separated by commas)
    sort: str
        the column to sort by

    Returns
    ----------
    articles : dict
        term to search on the news articles
