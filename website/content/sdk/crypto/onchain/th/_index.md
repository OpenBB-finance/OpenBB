To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### crypto.onchain.th(address, sortby: str = 'timestamp', ascend: bool = False) -> pandas.core.frame.DataFrame

Get info about token historical transactions. [Source: Ethplorer]

    Parameters
    ----------
    address: str
        Token e.g. 0xf3db5fa2c66b7af3eb0c0b782510816cbe4813b8
    sortby: str
        Key to sort by.
    ascend: str
        Sort in descending order.

    Returns
    -------
    pd.DataFrame:
        DataFrame with token historical transactions.

## Getting charts 
### crypto.onchain.th(address: str, limit: int = 10, sortby: str = 'timestamp', ascend: bool = False, hash_: bool = False, export: str = '', chart=True) -> None

Display info about token history. [Source: Ethplorer]

    Parameters
    ----------
    address: str
        Token balance e.g. 0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984
    limit: int
        Limit of transactions. Maximum 100
    sortby: str
        Key to sort by.
    ascend: str
        Sort in descending order.
    hash_: bool,
        Flag to show transaction hash.
    export : str
        Export dataframe data to csv,json,xlsx file
