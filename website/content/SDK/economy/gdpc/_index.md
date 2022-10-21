To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### economy.gdpc(start_year: int = 2010) -> pandas.core.frame.DataFrame

Real GDP per Capita for United States

    Parameters
    ----------
    start_year : int, optional
        Start year for plot, by default 2010

    Returns
    -------
    pd.DataFrame
        DataFrame of GDP per Capita

## Getting charts 
### economy.gdpc(start_year: int = 2010, raw: bool = False, export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True)

Display US GDP per Capita from AlphaVantage

    Parameters
    ----------
    start_year : int, optional
        Start year for plot, by default 2010
    raw : bool, optional
        Flag to show raw data, by default False
    export : str, optional
        Format to export data, by default
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
