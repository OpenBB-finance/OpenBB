## Get underlying data 
### crypto.load(symbol: 'str', start_date: 'datetime' = datetime.datetime(2019, 10, 7, 7, 55, 32, 347659), interval: 'str' = '1440', exchange: 'str' = 'binance', vs_currency: 'str' = 'usdt', end_date: 'datetime' = datetime.datetime(2022, 10, 11, 7, 55, 32, 347665), source: 'str' = 'CCXT') -> 'pd.DataFrame'

Load crypto currency to perform analysis on CoinGecko is used as source for price and
    YahooFinance for volume.

    Parameters
    ----------
    symbol: str
        Coin to get
    vs: str
        Quote Currency (usd or eur), by default usd
    days: int
        Data up to number of days ago, by default 365

    Returns
    -------
    pd.DataFrame
        Dataframe consisting of price and volume data
