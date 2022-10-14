To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### crypto.onchain.top(sortby: str = 'rank', ascend: bool = False) -> pandas.core.frame.DataFrame

Get top 50 tokens. [Source: Ethplorer]

    Returns
    -------
    pd.DataFrame:
        DataFrame with list of top 50 tokens.

## Getting charts 
### crypto.onchain.top(limit: int = 15, sortby: str = 'rank', ascend: bool = True, export: str = '', chart=True) -> None

Display top ERC20 tokens [Source: Ethplorer]

    Parameters
    ----------
    limit: int
        Limit of transactions. Maximum 100
    sortby: str
        Key to sort by.
    ascend: str
        Sort in descending order.
    export : str
        Export dataframe data to csv,json,xlsx file
