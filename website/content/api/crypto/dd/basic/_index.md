To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### crypto.dd.basic(symbol: str = 'btc-bitcoin') -> pandas.core.frame.DataFrame

Basic coin information [Source: CoinPaprika]

    Parameters
    ----------
    symbol: str
        Coin id

    Returns
    -------
    pd.DataFrame
        Metric, Value

## Getting charts 
### crypto.dd.basic(symbol: str = 'BTC', export: str = '', chart=True) -> None

Get basic information for coin. Like:
        name, symbol, rank, type, description, platform, proof_type, contract, tags, parent.
        [Source: CoinPaprika]

    Parameters
    ----------
    symbol: str
        Cryptocurrency symbol (e.g. BTC)
    export: str
        Export dataframe data to csv,json,xlsx
