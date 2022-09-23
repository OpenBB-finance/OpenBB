To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### crypto.ov.cpexchanges(symbols: str = 'USD', sortby: str = 'rank', ascend: bool = True) -> pandas.core.frame.DataFrame


    List exchanges from CoinPaprika API [Source: CoinPaprika]

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
        rank, name, currencies, markets, fiats, confidence_score, reported_volume_24h,
        reported_volume_7d ,reported_volume_30d, sessions_per_month,

## Getting charts 
### crypto.ov.cpexchanges(symbol: str, sortby: str = 'rank', ascend: bool = True, limit: int = 15, export: str = '', chart=True) -> None

List exchanges from CoinPaprika API. [Source: CoinPaprika]

    Parameters
    ----------
    currency: str
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

