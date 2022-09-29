To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### crypto.dd.candles(symbol: str, interval: str = '24h') -> pandas.core.frame.DataFrame

Get candles for chosen trading pair and time interval. [Source: Coinbase]

    Parameters
    ----------
    symbol: str
        Trading pair of coins on Coinbase e.g ETH-USDT or UNI-ETH
    interval: str
        Time interval. One from 1min, 5min ,15min, 1hour, 6hour, 24hour

    Returns
    -------
    pd.DataFrame
        Candles for chosen trading pair.

## Getting charts 
### crypto.dd.candles(symbol: str, interval: str = '24h', export: str = '', chart=True) -> None

Get candles for chosen trading pair and time interval. [Source: Coinbase]

    Parameters
    ----------
    symbol: str
        Trading pair of coins on Coinbase e.g ETH-USDT or UNI-ETH
    interval: str
        Time interval. One from 1m, 5m ,15m, 1h, 6h, 24h
    export : str
        Export dataframe data to csv,json,xlsx file
