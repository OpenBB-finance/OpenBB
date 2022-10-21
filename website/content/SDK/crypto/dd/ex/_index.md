To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### crypto.dd.ex(symbol: str = 'eth-ethereum', sortby: str = 'adjusted_volume_24h_share', ascend: bool = True) -> pandas.core.frame.DataFrame

Get all exchanges for given coin id. [Source: CoinPaprika]

    Parameters
    ----------
    symbol: str
        Identifier of Coin from CoinPaprika
    sortby: str
        Key by which to sort data. Every column name is valid (see for possible values:
        https://api.coinpaprika.com/v1).
    ascend: bool
        Flag to sort data ascending

    Returns
    -------
    pandas.DataFrame
        All exchanges for given coin
        Columns: id, name, adjusted_volume_24h_share, fiats

## Getting charts 
### crypto.dd.ex(symbol: str = 'btc', limit: int = 10, sortby: str = 'adjusted_volume_24h_share', ascend: bool = True, export: str = '', chart=True) -> None

Get all exchanges for given coin id. [Source: CoinPaprika]

    Parameters
    ----------
    symbol: str
        Cryptocurrency symbol (e.g. BTC)
    limit: int
        Number of records to display
    sortby: str
        Key by which to sort data. Every column name is valid (see for possible values:
        https://api.coinpaprika.com/v1).
    ascend: bool
        Flag to sort data ascending
    export : str
        Export dataframe data to csv,json,xlsx file
