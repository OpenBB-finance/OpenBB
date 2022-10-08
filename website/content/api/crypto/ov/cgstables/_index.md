To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### crypto.ov.cgstables(limit: int = 20, sortby: str = 'rank', ascend: bool = False) -> pandas.core.frame.DataFrame

Returns top stable coins [Source: CoinGecko]

    Parameters
    ----------
    limit: int
        How many rows to show
    sortby: str
        Key by which to sort data
    ascend: bool
        Flag to sort data ascending

    Returns
    -------
    pandas.DataFrame
        Rank, Name, Symbol, Price, Change_24h, Exchanges, Market_Cap, Change_30d, Url

## Getting charts 
### crypto.ov.cgstables(limit: int = 15, export: str = '', sortby: str = 'rank', ascend: bool = False, pie: bool = False, chart=True) -> None

Shows stablecoins data [Source: CoinGecko]

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
    pie : bool
        Whether to show a pie chart
