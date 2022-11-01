## Get underlying data 
### crypto.load(symbol: 'str', start_date: 'datetime' = datetime.datetime(2019, 10, 22, 11, 40, 0, 303083), interval: 'str' = '1440', exchange: 'str' = 'binance', vs_currency: 'str' = 'usdt', end_date: 'datetime' = datetime.datetime(2022, 10, 26, 11, 40, 0, 303103), source: 'str' = 'CCXT') -> 'pd.DataFrame'

Load crypto currency to get data for.

    Parameters
    ----------
    symbol: str
        Coin to get
    start_date: datetime
        The datetime to start at
    interval: str
        The interval between data points in minutes.
        Choose from: 1, 15, 30, 60, 240, 1440, 10080, 43200
    exchange: str:
        The exchange to get data from.
    vs_currency: str
        Quote Currency (Defaults to usdt)
    end_date: datetime
       The datetime to end at
    source: str
        The source of the data
        Choose from: CCXT, CoinGecko, YahooFinance

    Returns
    -------
    pd.DataFrame
        Dataframe consisting of price and volume data
