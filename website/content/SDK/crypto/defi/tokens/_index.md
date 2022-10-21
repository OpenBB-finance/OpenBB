To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### crypto.defi.tokens(skip: int = 0, limit: int = 100, sortby: str = 'index', ascend: bool = False) -> pandas.core.frame.DataFrame

Get list of tokens trade-able on Uniswap DEX. [Source: https://thegraph.com/en/]

    Parameters
    ----------
    skip: int
        Skip n number of records.
    limit: int
        Show n number of records.
    sortby: str
        The column to sort by
    ascend: bool
        Whether to sort in ascending order

    Returns
    -------
    pd.DataFrame
        Uniswap tokens with trading volume, transaction count, liquidity.

## Getting charts 
### crypto.defi.tokens(skip: int = 0, limit: int = 20, sortby: str = 'index', ascend: bool = False, export: str = '', chart=True) -> None

Displays tokens trade-able on Uniswap DEX.
    [Source: https://thegraph.com/en/]

    Parameters
    ----------
    skip: int
        Number of records to skip
    limit: int
        Number of records to display
    sortby: str
        Key by which to sort data
    ascend: bool
        Flag to sort data descending
    export : str
        Export dataframe data to csv,json,xlsx file
