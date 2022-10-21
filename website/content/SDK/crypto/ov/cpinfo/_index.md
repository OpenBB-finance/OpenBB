To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### crypto.ov.cpinfo(symbols: str = 'USD', sortby: str = 'rank', ascend: bool = True) -> pandas.core.frame.DataFrame

Returns basic coin information for all coins from CoinPaprika API [Source: CoinPaprika]

    Parameters
    ----------
    symbols: str
        Comma separated quotes to return e.g quotes=USD,BTC
    sortby: str
        Key by which to sort data
    ascend: bool
        Flag to sort data descending

    Returns
    -------
    pandas.DataFrame
        rank, name, symbol, price, volume_24h, circulating_supply, total_supply,
        max_supply, market_cap, beta_value, ath_price,

## Getting charts 
### crypto.ov.cpinfo(symbol: str, sortby: str = 'rank', ascend: bool = True, limit: int = 15, export: str = '', chart=True) -> None

Displays basic coin information for all coins from CoinPaprika API. [Source: CoinPaprika]

    Parameters
    ----------
    symbol: str
        Quoted currency
    limit: int
        Number of records to display
    sortby: str
        Key by which to sort data
    ascend: bool
        Flag to sort data descending
    links: bool
        Flag to display urls
    export : str
        Export dataframe data to csv,json,xlsx file
