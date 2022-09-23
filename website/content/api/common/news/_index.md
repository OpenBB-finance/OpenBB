# common.news

To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### common.news(term: str = '', sources: str = 'bloomberg.com') -> pandas.core.frame.DataFrame

Get news for a given term and source. [Source: Feedparser]

    Parameters
    ----------
    term : str
        term to search on the news articles
    sources: str
        sources to exclusively show news from

    Returns
    ----------
    articles : dict
        term to search on the news articles

## Getting charts 
### common.news(term: str, sources: str = '', limit: int = 5, export: str = '', chart=True)

Display news for a given term and source. [Source: Feedparser]

    Parameters
    ----------
    term : str
        term to search on the news articles
    sources : str
        sources to exclusively show news from
    limit : int
        number of articles to display
    export : str
        Export dataframe data to csv,json,xlsx file
