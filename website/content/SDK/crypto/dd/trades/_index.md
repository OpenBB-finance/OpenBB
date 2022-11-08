To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### crypto.dd.trades(exchange_id: str, symbol: str, to_symbol: str) -> pandas.core.frame.DataFrame

Returns trades for a coin in a given exchange
    [Source: https://docs.ccxt.com/en/latest/manual.html]

    Parameters
    ----------
    exchange_id : str
        exchange id
    symbol : str
        coin symbol
    to_symbol : str
        currency to compare coin against

    Returns
    -------
    pd.DataFrame
        trades for a coin in a given exchange

## Getting charts 
### crypto.dd.trades(exchange: str, symbol: str, to_symbol: str, limit: int = 10, export: str = '', chart=True)

Displays trades for a coin in a given exchange
    [Source: https://docs.ccxt.com/en/latest/manual.html]

    Parameters
    ----------
    exchange : str
        exchange id
    symbol : str
        coin symbol
    to_symbol : str
        currency to compare coin against
    limit : int
        number of trades to display
    export : str
        Export dataframe data to csv,json,xlsx file
