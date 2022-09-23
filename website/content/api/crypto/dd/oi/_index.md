To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### crypto.dd.oi(symbol: str, interval: int = 0) -> pandas.core.frame.DataFrame

Returns open interest by exchange for a certain symbol
    [Source: https://coinglass.github.io/API-Reference/]

    Parameters
    ----------
    symbol : str
        Crypto Symbol to search open interest futures (e.g., BTC)
    interval : int
        Frequency (possible values are: 0 for ALL, 2 for 1H, 1 for 4H, 4 for 12H), by default 0

    Returns
    -------
    pd.DataFrame
        open interest by exchange and price

## Getting charts 
### crypto.dd.oi(symbol: str, interval: int = 0, export: str = '', chart=True) -> None

Displays open interest by exchange for a certain cryptocurrency
    [Source: https://coinglass.github.io/API-Reference/]

    Parameters
    ----------
    symbol : str
        Crypto symbol to search open interest (e.g., BTC)
    interval : int
        Frequency (possible values are: 0 for ALL, 2 for 1H, 1 for 4H, 4 for 12H), by default 0
    export : str
        Export dataframe data to csv,json,xlsx
