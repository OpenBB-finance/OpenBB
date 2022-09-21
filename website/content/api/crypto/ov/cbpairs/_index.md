# crypto.ov.cbpairs

To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
###crypto.ov.cbpairs(top: int = 50, sortby: str = 'quote_increment', ascend: bool = True) -> pandas.core.frame.DataFrame

Get a list of available currency pairs for trading. [Source: Coinbase]

    base_min_size - min order size
    base_max_size - max order size
    min_market_funds -  min funds allowed in a market order.
    max_market_funds - max funds allowed in a market order.

    Parameters
    ----------
    top: int
        Top n of pairs
    sortby: str
        Key to sortby data
    ascend: bool
        Sort descending flag

    Returns
    -------
    pd.DataFrame
        Available trading pairs on Coinbase

## Getting charts 
###crypto.ov.cbpairs(top: int = 20, sortby: str = 'quote_increment', ascend: bool = True, export: str = '', chart=True) -> None

Displays a list of available currency pairs for trading. [Source: Coinbase]

    Parameters
    ----------
    top: int
        Top n of pairs
    sortby: str
        Key to sortby data
    ascend: bool
        Sort ascending flag
    export : str
        Export dataframe data to csv,json,xlsx file
