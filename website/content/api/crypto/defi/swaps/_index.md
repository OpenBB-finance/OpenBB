To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### crypto.defi.swaps(limit: int = 100) -> pandas.core.frame.DataFrame

Get the last 100 swaps done on Uniswap [Source: https://thegraph.com/en/]

    Parameters
    -------
    limit: int
        Number of swaps to return. Maximum possible number: 1000.
    Returns
    -------
    pd.DataFrame
        Last 100 swaps on Uniswap

## Getting charts 
### crypto.defi.swaps(limit: int = 10, sortby: str = 'timestamp', ascend: bool = False, export: str = '', chart=True) -> None

Displays last swaps done on Uniswap
    [Source: https://thegraph.com/en/]

    Parameters
    ----------
    limit: int
        Number of records to display
    sortby: str
        Key by which to sort data. The table can be sorted by every of its columns
        (see https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2).
    ascend: bool
        Flag to sort data descending
    export : str
        Export dataframe data to csv,json,xlsx file
