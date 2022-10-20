To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### economy.gdp(interval: str = 'q', start_year: int = 2010) -> pandas.core.frame.DataFrame

Get annual or quarterly Real GDP for US

    Parameters
    ----------
    interval : str, optional
        Interval for GDP, by default "a" for annual, by default "q"
    start_year : int, optional
        Start year for plot, by default 2010
    Returns
    -------
    pd.DataFrame
        Dataframe of GDP

## Getting charts 
### economy.gdp(interval: str = 'q', start_year: int = 2010, raw: bool = False, export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True)

Display US GDP from AlphaVantage

    Parameters
    ----------
    interval : str
        Interval for GDP.  Either "a" or "q", by default "q"
    start_year : int, optional
        Start year for plot, by default 2010
    raw : bool, optional
        Flag to show raw data, by default False
    export : str, optional
        Format to export data, by default ""
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
