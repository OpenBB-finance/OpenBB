To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### crypto.onchain.ttcp(network: str = 'ethereum', exchange: str = 'Uniswap', limit: int = 90, sortby: str = 'tradeAmount', ascend: bool = True) -> pandas.core.frame.DataFrame

Get most traded crypto pairs on given decentralized exchange in chosen time period.
    [Source: https://graphql.bitquery.io/]

    Parameters
    ----------
    network: str
        EVM network. One from list: bsc (binance smart chain), ethereum or matic
    exchange:
        Decentralized exchange name
    limit:
        Number of days taken into calculation account.
    sortby: str
        Key by which to sort data
    ascend: bool
        Flag to sort data ascending

    Returns
    -------


## Getting charts 
### crypto.onchain.ttcp(exchange='Uniswap', days: int = 10, limit: int = 10, sortby: str = 'tradeAmount', ascend: bool = True, export: str = '', chart=True) -> None

Display most traded crypto pairs on given decentralized exchange in chosen time period.
     [Source: https://graphql.bitquery.io/]

    Parameters
    ----------
    exchange:
        Decentralized exchange name
    days:
        Number of days taken into calculation account.
    sortby: str
        Key by which to sort data
    ascend: bool
        Flag to sort data ascending
    export : str
        Export dataframe data to csv,json,xlsx file
    Returns
    -------
    pd.DataFrame
        Most traded crypto pairs on given decentralized exchange in chosen time period.
