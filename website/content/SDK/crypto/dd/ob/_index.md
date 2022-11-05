To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### crypto.dd.ob(exchange_id: str, symbol: str, to_symbol: str) -> Dict

Returns orderbook for a coin in a given exchange
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
    Dict with bids and asks

## Getting charts 
### crypto.dd.ob(exchange: str, symbol: str, to_symbol: str, export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True)

Displays order book for a coin in a given exchange
    [Source: https://docs.ccxt.com/en/latest/manual.html]

    Parameters
    ----------
    exchange : str
        exchange id
    symbol : str
        coin symbol
    vs : str
        currency to compare coin against
    export : str
        Export dataframe data to csv,json,xlsx file
