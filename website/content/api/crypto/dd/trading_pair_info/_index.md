## Get underlying data 
### crypto.dd.trading_pair_info(symbol: str) -> pandas.core.frame.DataFrame

Get information about chosen trading pair. [Source: Coinbase]

    Parameters
    ----------
    symbol: str
        Trading pair of coins on Coinbase e.g ETH-USDT or UNI-ETH

    Returns
    -------
    pd.DataFrame
        Basic information about given trading pair
