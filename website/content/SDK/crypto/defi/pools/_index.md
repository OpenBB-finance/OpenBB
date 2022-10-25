To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### crypto.defi.pools() -> pandas.core.frame.DataFrame

Get uniswap pools by volume. [Source: https://thegraph.com/en/]

    Returns
    -------
    pd.DataFrame
        Trade-able pairs listed on Uniswap by top volume.

## Getting charts 
### crypto.defi.pools(limit: int = 20, sortby: str = 'volumeUSD', ascend: bool = True, export: str = '', chart=True) -> None

Displays uniswap pools by volume.
    [Source: https://thegraph.com/en/]

    Parameters
    ----------
    limit: int
        Number of records to display
    sortby: str
        Key by which to sort data. The table can be sorted by every of its columns
        (see https://bit.ly/3ORagr1 then press ctrl-enter or execute the query).
    ascend: bool
        Flag to sort data descending
    export : str
        Export dataframe data to csv,json,xlsx file
