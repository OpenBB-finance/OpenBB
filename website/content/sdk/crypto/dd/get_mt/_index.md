To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### crypto.dd.get_mt(only_free: bool = True) -> pandas.core.frame.DataFrame

Returns available messari timeseries
    [Source: https://messari.io/]

    Parameters
    ----------
    only_free : bool
        Display only timeseries available for free

    Returns
    -------
    pd.DataFrame
        available timeseries

## Getting charts 
### crypto.dd.get_mt(limit: int = 10, query: str = '', only_free: bool = True, export: str = '', chart=True) -> None

Display messari timeseries list
    [Source: https://messari.io/]

    Parameters
    ----------
    limit : int
        number to show
    query : str
        Query to search across all messari timeseries
    only_free : bool
        Display only timeseries available for free
    export : str
        Export dataframe data to csv,json,xlsx file
