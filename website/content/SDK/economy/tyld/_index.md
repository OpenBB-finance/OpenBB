To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### economy.tyld(interval: str = 'm', maturity: str = '10y', start_date: str = '2010-01-01') -> pandas.core.frame.DataFrame

Get historical yield for a given maturity

    Parameters
    ----------
    interval : str
        Interval for data.  Can be "d","w","m" for daily, weekly or monthly, by default "m"
    start_date: str
        Start date for data.  Should be in YYYY-MM-DD format, by default "2010-01-01"
    maturity : str
        Maturity timeline.  Can be "3mo","5y","10y" or "30y", by default "10y"

    Returns
    -------
    pd.DataFrame
        Dataframe of historical yields

## Getting charts 
### economy.tyld(interval: str = 'm', maturity: str = '10y', start_date: str = '2010-01-01', raw: bool = False, export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True)

Display historical treasury yield for given maturity

    Parameters
    ----------
    interval : str
        Interval for data.  Can be "d","w","m" for daily, weekly or monthly, by default "m"
    maturity : str
        Maturity timeline.  Can be "3mo","5y","10y" or "30y", by default "10y"
    start_date: str
        Start date for data.  Should be in YYYY-MM-DD format, by default "2010-01-01"
    raw : bool, optional
        Flag to display raw data, by default False
    export : str, optional
        Format to export data, by default ""
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
