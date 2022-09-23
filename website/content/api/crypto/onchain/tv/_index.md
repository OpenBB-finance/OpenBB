To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### crypto.onchain.tv(symbol: str = 'UNI', trade_amount_currency: str = 'USD', sortby: str = 'tradeAmount', ascend: bool = True) -> pandas.core.frame.DataFrame

Get token volume on different Decentralized Exchanges. [Source: https://graphql.bitquery.io/]

    Parameters
    ----------
    symbol: str
        ERC20 token symbol.
    trade_amount_currency: str
        Currency to display trade amount in.
    sortby: str
        Key by which to sort data
    ascend: bool
        Flag to sort data ascending

    Returns
    -------
    pd.DataFrame
        Token volume on Decentralized Exchanges

## Getting charts 
### crypto.onchain.tv(symbol: str = 'WBTC', trade_amount_currency: str = 'USD', limit: int = 10, sortby: str = 'tradeAmount', ascend: bool = True, export: str = '', chart=True) -> None

Display token volume on different Decentralized Exchanges.
    [Source: https://graphql.bitquery.io/]

    Parameters
    ----------
    symbol: str
        ERC20 token symbol or address
    trade_amount_currency: str
        Currency of displayed trade amount. Default: USD
    limit: int
        Number of records to display
    sortby: str
        Key by which to sort data
    ascend: bool
        Flag to sort data ascending
    export : str
        Export dataframe data to csv,json,xlsx file
    Returns
    -------
    pd.DataFrame
        Token volume on different decentralized exchanges
