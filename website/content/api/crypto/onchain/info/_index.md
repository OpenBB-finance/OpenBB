To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### crypto.onchain.info(address) -> pandas.core.frame.DataFrame

Get info about ERC20 token. [Source: Ethplorer]

    Parameters
    ----------
    address: str
        Token balance e.g. 0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984

    Returns
    -------
    pd.DataFrame:
        DataFrame with information about provided ERC20 token.

## Getting charts 
### crypto.onchain.info(address: str, social: bool = False, export: str = '', chart=True) -> None

Display info about ERC20 token. [Source: Ethplorer]

    Parameters
    ----------
    address: str
        Token balance e.g. 0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984
    social: bool
        Flag to display social media links
    export : str
        Export dataframe data to csv,json,xlsx file
