To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### crypto.onchain.holders(address, sortby: str = 'balance', ascend: bool = True) -> pandas.core.frame.DataFrame

Get info about top token holders. [Source: Ethplorer]

    Parameters
    ----------
    address: str
        Token balance e.g. 0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984
    sortby: str
        Key to sort by.
    ascend: str
        Sort in descending order.

    Returns
    -------
    pd.DataFrame:
        DataFrame with list of top token holders.

## Getting charts 
### crypto.onchain.holders(address: str, limit: int = 10, sortby: str = 'balance', ascend: bool = True, export: str = '', chart=True) -> None

Display info about top ERC20 token holders. [Source: Ethplorer]

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
    export : str
        Export dataframe data to csv,json,xlsx file
