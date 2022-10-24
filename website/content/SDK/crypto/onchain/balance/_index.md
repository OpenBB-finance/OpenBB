To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### crypto.onchain.balance(address: str, sortby: str = 'index', ascend: bool = False) -> pandas.core.frame.DataFrame

Get info about tokens on you ethereum blockchain balance. Eth balance, balance of all tokens which
    have name and symbol. [Source: Ethplorer]

    Parameters
    ----------
    address: str
        Blockchain balance e.g. 0x3cD751E6b0078Be393132286c442345e5DC49699
    sortby: str
        Key to sort by.
    ascend: str
        Sort in descending order.

    Returns
    -------
    pd.DataFrame:
        DataFrame with list of tokens and their balances.

## Getting charts 
### crypto.onchain.balance(address: str, limit: int = 15, sortby: str = 'index', ascend: bool = False, export: str = '', chart=True) -> None

Display info about tokens for given ethereum blockchain balance e.g. ETH balance,
    balance of all tokens with name and symbol. [Source: Ethplorer]

    Parameters
    ----------
    address: str
        Ethereum balance.
    limit: int
        Limit of transactions. Maximum 100
    sortby: str
        Key to sort by.
    ascend: str
        Sort in descending order.
    export : str
        Export dataframe data to csv,json,xlsx file
