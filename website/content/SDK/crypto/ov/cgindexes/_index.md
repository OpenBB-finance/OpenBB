To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### crypto.ov.cgindexes(sortby: str = 'Name', ascend: bool = True) -> pandas.core.frame.DataFrame

Get list of crypto indexes from CoinGecko API [Source: CoinGecko]

    Returns
    -------
    pandas.DataFrame
        Name, Id, Market, Last, MultiAsset
    sortby: str
        Key by which to sort data
    ascend: bool
        Flag to sort data descending

## Getting charts 
### crypto.ov.cgindexes(sortby: str = 'Name', ascend: bool = True, limit: int = 15, export: str = '', chart=True) -> None

Shows list of crypto indexes. [Source: CoinGecko]

    Parameters
    ----------
    limit: int
        Number of records to display
    sortby: str
        Key by which to sort data
    ascend: bool
        Flag to sort data descending
    export : str
        Export dataframe data to csv,json,xlsx file
