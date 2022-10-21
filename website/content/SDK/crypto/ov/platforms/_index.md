To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### crypto.ov.platforms(sortby: str = 'Name', ascend: bool = True) -> pandas.core.frame.DataFrame

Get list of financial platforms from CoinGecko API [Source: CoinGecko]

    Parameter
    ----------
    sortby: str
        Key by which to sort data
    ascend: bool
        Flag to sort data ascending

    Returns
    -------
    pandas.DataFrame
        Rank, Name, Category, Centralized, Url

## Getting charts 
### crypto.ov.platforms(sortby: str = 'Name', ascend: bool = True, limit: int = 15, export: str = '', chart=True) -> None

Shows list of financial platforms. [Source: CoinGecko]

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
