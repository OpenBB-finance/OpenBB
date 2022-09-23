To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### crypto.ov.cgexrates(sortby: str = 'Name', ascend: bool = False) -> pandas.core.frame.DataFrame

Get list of crypto, fiats, commodity exchange rates from CoinGecko API [Source: CoinGecko]

    Parameters
    ----------
    sortby: str
        Key by which to sort data
    ascend: bool
        Flag to sort data ascending

    Returns
    -------
    pandas.DataFrame
        Index, Name, Unit, Value, Type

## Getting charts 
### crypto.ov.cgexrates(sortby: str = 'Name', ascend: bool = False, limit: int = 15, export: str = '', chart=True) -> None

Shows  list of crypto, fiats, commodity exchange rates. [Source: CoinGecko]

    Parameters
    ----------
    limit: int
        Number of records to display
    sortby: str
        Key by which to sort data
    ascend: bool
        Flag to sort data ascending
    export : str
        Export dataframe data to csv,json,xlsx file
