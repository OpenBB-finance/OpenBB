To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### crypto.disc.losers(interval: str = '1h', limit: int = 50, sortby: str = 'market_cap_rank') -> pandas.core.frame.DataFrame

Shows Largest Losers - coins which lose the most in given period. [Source: CoinGecko]

    Parameters
    ----------
    interval: str
        Time interval by which data is displayed. One from [1h, 24h, 7d, 14d, 30d, 60d, 1y]
    limit: int
        Number of records to display
    sortby: str
        Key to sort data. The table can be sorted by every of its columns. Refer to
        API documentation (see /coins/markets in https://www.coingecko.com/en/api/documentation)

    Returns
    -------
    pd.DataFrame
        Top Losers  - coins which lost most in price in given period of time.
        Columns: Symbol, Name, Volume, Price, %Change_{interval}, Url

## Getting charts 
### crypto.disc.losers(interval: str = '1h', limit: int = 20, export: str = '', sortby: str = 'Market Cap Rank', chart=True) -> None

Shows Largest Losers - coins which lost the most in given period of time. [Source: CoinGecko]

    Parameters
    ----------
    interval: str
        Time period by which data is displayed. One from [1h, 24h, 7d, 14d, 30d, 60d, 1y]
    limit: int
        Number of records to display
    sortby: str
        Key to sort data. The table can be sorted by every of its columns. Refer to
        API documentation (see /coins/markets in https://www.coingecko.com/en/api/documentation)
    export : str
        Export dataframe data to csv,json,xlsx file
