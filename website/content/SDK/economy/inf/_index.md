To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### economy.inf(start_year: int = 2010) -> pandas.core.frame.DataFrame

Get historical Inflation for United States from AlphaVantage

    Parameters
    ----------
    start_year : int, optional
        Start year for plot, by default 2010

    Returns
    -------
    pd.DataFrame
        DataFrame of inflation rates

## Getting charts 
### economy.inf(start_year: int = 2010, raw: bool = False, export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True)

Display US Inflation from AlphaVantage

    Parameters
    ----------
    start_year : int, optional
        Start year for plot, by default 2010
    raw : bool, optional
        Flag to show raw data, by default False
    export : str, optional
        Format to export data, by default ""
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
