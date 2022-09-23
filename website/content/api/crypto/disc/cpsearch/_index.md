To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### crypto.disc.cpsearch(query: str, category: Optional[Any] = None, modifier: Optional[Any] = None, sortby: str = 'id', ascend: bool = True) -> pandas.core.frame.DataFrame

Search CoinPaprika. [Source: CoinPaprika]

    Parameters
    ----------
    query:  str
        phrase for search
    category:  Optional[Any]
        one or more categories (comma separated) to search.
        Available options: currencies|exchanges|icos|people|tags
        Default: currencies,exchanges,icos,people,tags
    modifier: Optional[Any]
        set modifier for search results. Available options: symbol_search -
        search only by symbol (works for currencies only)
    sortby: str
        Key to sort data. The table can be sorted by every of its columns. Refer to
        API documentation (see https://api.coinpaprika.com/docs#tag/Tools/paths/~1search/get)
    ascend: bool
        Flag to sort data descending

    Returns
    -------
    pandas.DataFrame
        Search Results
        Columns: Metric, Value

## Getting charts 
### crypto.disc.cpsearch(query: str, category: str = 'all', limit: int = 10, sortby: str = 'id', ascend: bool = True, export: str = '', chart=True) -> None

Search over CoinPaprika. [Source: CoinPaprika]

    Parameters
    ----------
    query: str
        Search query
    category: str
        Categories to search: currencies|exchanges|icos|people|tags|all. Default: all
    limit: int
        Number of records to display
    sortby: str
        Key to sort data. The table can be sorted by every of its columns. Refer to
        API documentation (see https://api.coinpaprika.com/docs#tag/Tools/paths/~1search/get)
    ascend: bool
        Flag to sort data descending
    export : str
        Export dataframe data to csv,json,xlsx file
