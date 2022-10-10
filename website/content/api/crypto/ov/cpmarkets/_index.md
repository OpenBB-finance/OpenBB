To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### crypto.ov.cpmarkets(symbols: str = 'USD', sortby: str = 'rank', ascend: bool = True) -> pandas.core.frame.DataFrame

Returns basic coin information for all coins from CoinPaprika API [Source: CoinPaprika]

    Parameters
    ----------
    symbols: str
        Comma separated quotes to return e.g quotes=USD,BTC
    sortby: str
        Key by which to sort data
    ascend: bool
        Flag to sort data ascend

    Returns
    -------
    pandas.DataFrame
        rank, name, symbol, price, volume_24h, mcap_change_24h,
        pct_change_1h, pct_change_24h, ath_price, pct_from_ath,

## Getting charts 
### crypto.ov.cpmarkets(symbol: str, sortby: str = 'rank', ascend: bool = True, limit: int = 15, export: str = '', chart=True) -> None

Displays basic market information for all coins from CoinPaprika API. [Source: CoinPaprika]

    Parameters
    ----------
    symbol: str
        Quoted currency
    limit: int
        Number of records to display
    sortby: str
        Key by which to sort data
    ascend: bool
        Flag to sort data ascending
    links: bool
        Flag to display urls
    export : str
        Export dataframe data to csv,json,xlsx file
