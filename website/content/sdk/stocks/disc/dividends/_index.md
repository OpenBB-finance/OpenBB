## Get underlying data 
### stocks.disc.dividends(date: str = '2022-10-18') -> pandas.core.frame.DataFrame

Gets dividend calendar for given date.  Date represents Ex-Dividend Date

    Parameters
    ----------
    date: datetime
        Date to get for in format YYYY-MM-DD

    Returns
    -------
    pd.DataFrame:
        Dataframe of dividend calendar
