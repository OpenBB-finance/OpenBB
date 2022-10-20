To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### economy.cpi(interval: str = 'm', start_year: int = 2010) -> pandas.core.frame.DataFrame

Get Consumer Price Index from Alpha Vantage

    Parameters
    ----------
    interval : str
        Interval for data.  Either "m" or "s" for monthly or semiannual
    start_year : int, optional
        Start year for plot, by default 2010

    Returns
    -------
    pd.DataFrame
        Dataframe of CPI

## Getting charts 
### economy.cpi(interval: str = 'm', start_year: int = 2010, raw: bool = False, export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True)

Display US consumer price index (CPI) from AlphaVantage

    Parameters
    ----------
    interval : str
        Interval for GDP.  Either "m" or "s"
    start_year : int, optional
        Start year for plot, by default 2010
    raw : bool, optional
        Flag to show raw data, by default False
    export : str, optional
        Format to export data, by default ""
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
