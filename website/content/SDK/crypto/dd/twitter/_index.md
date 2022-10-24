To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### crypto.dd.twitter(symbol: str = 'eth-ethereum', sortby: str = 'date', ascend: bool = True) -> pandas.core.frame.DataFrame

Get twitter timeline for given coin id. Not more than last 50 tweets [Source: CoinPaprika]

    Parameters
    ----------
    symbol: str
        id of coin from coinpaprika e.g. Ethereum - > 'eth-ethereum'
    sortby: str
        Key by which to sort data. Every column name is valid
        (see for possible values:
        https://api.coinpaprika.com/docs#tag/Coins/paths/~1coins~1%7Bcoin_id%7D~1twitter/get).
    ascend: bool
        Flag to sort data descending
    Returns
    -------
    pandas.DataFrame
        Twitter timeline for given coin.
        Columns: date, user_name, status, retweet_count, like_count

## Getting charts 
### crypto.dd.twitter(symbol: str = 'BTC', limit: int = 10, sortby: str = 'date', ascend: bool = True, export: str = '', chart=True) -> None

Get twitter timeline for given coin id. Not more than last 50 tweets [Source: CoinPaprika]

    Parameters
    ----------
    symbol: str
        Cryptocurrency symbol (e.g. BTC)
    limit: int
        Number of records to display
    sortby: str
        Key by which to sort data. Every column name is valid
        (see for possible values:
        https://api.coinpaprika.com/docs#tag/Coins/paths/~1coins~1%7Bcoin_id%7D~1twitter/get).
    ascend: bool
        Flag to sort data ascending
    export : str
        Export dataframe data to csv,json,xlsx file
