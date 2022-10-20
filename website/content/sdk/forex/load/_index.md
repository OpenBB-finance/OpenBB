## Get underlying data 
### forex.load(to_symbol: str, from_symbol: str, resolution: str = 'd', interval: str = '1day', start_date: str = '2021-10-20', source: str = 'YahooFinance') -> pandas.core.frame.DataFrame

Loads forex for two given symbols

    Parameters
    ----------
    to_symbol : str
        The from currency symbol. Ex: USD, EUR, GBP, YEN
    from_symbol: str
        The from currency symbol. Ex: USD, EUR, GBP, YEN
    resolution: str
        The resolution for the data
    interval: str
        What interval to get data for
    start_date: str
        When to begin loading in data
    source: str
        Where to get data from

    Returns
    -------
    pd.DataFrame
        The loaded data
