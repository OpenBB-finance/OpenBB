To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### crypto.dd.balance(from_symbol: str, to_symbol: str = 'USDT') -> pandas.core.frame.DataFrame

Get account holdings for asset. [Source: Binance]

    Parameters
    ----------
    from_symbol: str
        Cryptocurrency
    to_symbol: str
        Cryptocurrency

    Returns
    -------
    pd.DataFrame
        Dataframe with account holdings for an asset

## Getting charts 
### crypto.dd.balance(from_symbol: str, to_symbol: str = 'USDT', export: str = '', chart=True) -> None

Get account holdings for asset. [Source: Binance]

    Parameters
    ----------
    from_symbol: str
        Cryptocurrency
    to_symbol: str
        Cryptocurrency
    export: str
        Export dataframe data to csv,json,xlsx
