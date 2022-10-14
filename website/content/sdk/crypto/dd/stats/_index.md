To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### crypto.dd.stats(symbol: str) -> pandas.core.frame.DataFrame

Get 24 hr stats for the product. Volume is in base currency units.
    Open, high and low are in quote currency units.  [Source: Coinbase]

    Parameters
    ----------
    symbol: str
        Trading pair of coins on Coinbase e.g ETH-USDT or UNI-ETH

    Returns
    -------
    pd.DataFrame
        24h stats for chosen trading pair

## Getting charts 
### crypto.dd.stats(symbol: str, export: str = '', chart=True) -> None

Get 24 hr stats for the product. Volume is in base currency units.
    Open, high and low are in quote currency units.  [Source: Coinbase]

    Parameters
    ----------
    symbol: str
        Trading pair of coins on Coinbase e.g ETH-USDT or UNI-ETH
    export : str
        Export dataframe data to csv,json,xlsx file
