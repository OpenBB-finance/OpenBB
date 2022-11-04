## Get underlying data 
### economy.events(countries: Union[List[str], str] = '', start_date: str = '2022-11-04', end_date: str = '2022-11-04') -> pandas.core.frame.DataFrame

Get economic calendar for countries between specified dates

    Parameters
    ----------
    countries : [List[str],str]
        List of countries to include in calendar.  Empty returns all
    start_date : str
        Start date for calendar
    end_date : str
        End date for calendar

    Returns
    -------
    pd.DataFrame
        Economic calendar
