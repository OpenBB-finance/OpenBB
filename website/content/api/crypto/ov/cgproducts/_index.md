To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### crypto.ov.cgproducts(sortby: str = 'Name', ascend: bool = True) -> pandas.core.frame.DataFrame

Get list of financial products from CoinGecko API

    Parameters
    ----------
    sortby: str
        Key by which to sort data
    ascend: bool
        Flag to sort data ascending

    Returns
    -------
    pandas.DataFrame
       Rank,  Platform, Identifier, Supply_Rate, Borrow_Rate

## Getting charts 
### crypto.ov.cgproducts(sortby: str = 'Platform', ascend: bool = False, limit: int = 15, export: str = '', chart=True) -> None

Shows list of financial products. [Source: CoinGecko]

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
