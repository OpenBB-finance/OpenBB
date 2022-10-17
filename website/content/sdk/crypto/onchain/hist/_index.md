To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### crypto.onchain.hist(address, sortby: str = 'timestamp', ascend: bool = True) -> pandas.core.frame.DataFrame

Get information about balance historical transactions. [Source: Ethplorer]

    Parameters
    ----------
    address: str
        Blockchain balance e.g. 0x3cD751E6b0078Be393132286c442345e5DC49699
    sortby: str
        Key to sort by.
    ascend: str
        Sort in ascending order.

    Returns
    -------
    pd.DataFrame:
        DataFrame with balance historical transactions (last 100)

## Getting charts 
### crypto.onchain.hist(address: str, limit: int = 10, sortby: str = 'timestamp', ascend: bool = True, export: str = '', chart=True) -> None

Display information about balance historical transactions. [Source: Ethplorer]

    Parameters
    ----------
    address: str
        Ethereum blockchain balance e.g. 0x3cD751E6b0078Be393132286c442345e5DC49699
    limit: int
        Limit of transactions. Maximum 100
    sortby: str
        Key to sort by.
    ascend: str
        Sort in ascending order.
    export : str
        Export dataframe data to csv,json,xlsx file
