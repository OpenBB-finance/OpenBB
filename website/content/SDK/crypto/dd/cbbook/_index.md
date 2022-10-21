To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### crypto.dd.cbbook(symbol: str) -> Tuple[numpy.ndarray, numpy.ndarray, str, dict]

Get orders book for chosen trading pair. [Source: Coinbase]

    Parameters
    ----------
    symbol: str
        Trading pair of coins on Coinbase e.g ETH-USDT or UNI-ETH

    Returns
    -------
    Tuple[np.array, np.array, str, dict]
        array with bid prices, order sizes and cumulative order sizes
        array with ask prices, order sizes and cumulative order sizes
        trading pair
        dict with raw data

## Getting charts 
### crypto.dd.cbbook(symbol: str, export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True) -> None

Displays a list of available currency pairs for trading. [Source: Coinbase]

    Parameters
    ----------
    symbol: str
        Trading pair of coins on Coinbase e.g ETH-USDT or UNI-ETH
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
