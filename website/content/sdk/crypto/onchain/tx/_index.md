To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### crypto.onchain.tx(tx_hash) -> pandas.core.frame.DataFrame

Get info about transaction. [Source: Ethplorer]

    Parameters
    ----------
    tx_hash: str
        Transaction hash e.g. 0x9dc7b43ad4288c624fdd236b2ecb9f2b81c93e706b2ffd1d19b112c1df7849e6

    Returns
    -------
    pd.DataFrame:
        DataFrame with information about ERC20 token transaction.

## Getting charts 
### crypto.onchain.tx(tx_hash: str, export: str = '', chart=True) -> None

Display info about transaction. [Source: Ethplorer]

    Parameters
    ----------
    tx_hash: str
        Transaction hash e.g. 0x9dc7b43ad4288c624fdd236b2ecb9f2b81c93e706b2ffd1d19b112c1df7849e6
    export : str
        Export dataframe data to csv,json,xlsx file
