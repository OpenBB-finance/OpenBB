To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### crypto.dd.book(from_symbol: str, limit: int = 100, to_symbol: str = 'USDT') -> pandas.core.frame.DataFrame

Get order book for currency. [Source: Binance]

    Parameters
    ----------

    from_symbol: str
        Cryptocurrency symbol
    limit: int
        Limit parameter. Adjusts the weight
    to_symbol: str
        Quote currency (what to view coin vs)

    Returns
    -------

    pd.DataFrame
        Dataframe containing orderbook

## Getting charts 
### crypto.dd.book(from_symbol: str, limit: int = 100, to_symbol: str = 'USDT', export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True) -> None

Get order book for currency. [Source: Binance]

    Parameters
    ----------

    from_symbol: str
        Cryptocurrency symbol
    limit: int
        Limit parameter. Adjusts the weight
    to_symbol: str
        Quote currency (what to view coin vs)
    export: str
        Export dataframe data to csv,json,xlsx
    external_axes : Optional[List[plt.Axes]]
        External axes (1 axis is expected in the list), by default None
