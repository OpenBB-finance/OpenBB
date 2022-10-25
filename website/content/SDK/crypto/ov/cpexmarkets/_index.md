To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### crypto.ov.cpexmarkets(exchange_id: str = 'binance', symbols: str = 'USD', sortby: str = 'pair', ascend: bool = True) -> pandas.core.frame.DataFrame

List markets by exchange ID [Source: CoinPaprika]

    Parameters
    ----------
    exchange_id: str
        identifier of exchange e.g for Binance Exchange -> binance
    symbols: str
        Comma separated quotes to return e.g quotes=USD,BTC
    sortby: str
        Key by which to sort data
    ascend: bool
        Flag to sort data ascending

    Returns
    -------
    pandas.DataFrame
        pair, base_currency_name, quote_currency_name, market_url,
        category, reported_volume_24h_share, trust_score,

## Getting charts 
### crypto.ov.cpexmarkets(exchange: str = 'binance', sortby: str = 'pair', ascend: bool = True, limit: int = 15, links: bool = False, export: str = '', chart=True) -> None

Get all markets for given exchange [Source: CoinPaprika]

    Parameters
    ----------
    exchange: str
        Exchange identifier e.g Binance
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
