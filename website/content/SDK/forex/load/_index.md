## Get underlying data 
### forex.load(to_symbol: str, from_symbol: str, resolution: str = 'd', interval: str = '1day', start_date: str = '2021-11-03', source: str = 'YahooFinance', verbose: bool = True) -> pandas.core.frame.DataFrame

Load forex for two given symbols.

    Parameters
    ----------
    to_symbol : str
        The from currency symbol. Ex: USD, EUR, GBP, YEN
    from_symbol : str
        The from currency symbol. Ex: USD, EUR, GBP, YEN
    resolution : str, optional
        The resolution for the data, by default "d"
    interval : str, optional
        What interval to get data for, by default "1day"
    start_date : str, optional
        When to begin loading in data, by default last_year.strftime("%Y-%m-%d")
    source : str, optional
        Where to get data from, by default "YahooFinance"
    verbose : bool, optional
        Display verbose information on what was the pair that was loaded, by default True

    Returns
    -------
    pd.DataFrame
        The loaded data
