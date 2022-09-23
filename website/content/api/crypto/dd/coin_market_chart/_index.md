## Get underlying data 
### crypto.dd.coin_market_chart(symbol: str = '', vs_currency: str = 'usd', days: int = 30, **kwargs: Any) -> pandas.core.frame.DataFrame

Get prices for given coin. [Source: CoinGecko]

    Parameters
    ----------
    vs_currency: str
        currency vs which display data
    days: int
        number of days to display the data
    kwargs

    Returns
    -------
    pandas.DataFrame
        Prices for given coin
        Columns: time, price, currency
