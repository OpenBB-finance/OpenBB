To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### crypto.dd.trades(symbol: str, limit: int = 1000, side: Optional[Any] = None) -> pandas.core.frame.DataFrame

Get last N trades for chosen trading pair. [Source: Coinbase]

    Parameters
    ----------
    symbol: str
        Trading pair of coins on Coinbase e.g ETH-USDT or UNI-ETH
    limit: int
        Last <limit> of trades. Maximum is 1000.
    side: str
        You can chose either sell or buy side. If side is not set then all trades will be displayed.
    Returns
    -------
    pd.DataFrame
        Last N trades for chosen trading pairs.

## Getting charts 
### crypto.dd.trades(symbol: str, limit: int = 20, side: Optional[str] = None, export: str = '', chart=True) -> None

Display last N trades for chosen trading pair. [Source: Coinbase]

    Parameters
    ----------
    symbol: str
        Trading pair of coins on Coinbase e.g ETH-USDT or UNI-ETH
    limit: int
        Last <limit> of trades. Maximum is 1000.
    side: Optional[str]
        You can chose either sell or buy side. If side is not set then all trades will be displayed.
    export : str
        Export dataframe data to csv,json,xlsx file
