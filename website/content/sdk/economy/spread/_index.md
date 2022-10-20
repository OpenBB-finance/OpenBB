To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### economy.spread(countries: Union[str, List[str]] = 'G7', maturity: str = '10Y', change: bool = False) -> pandas.core.frame.DataFrame

Get spread matrix. [Source: Investing.com]

    Parameters
    ----------
    countries: Union[str, List[str]]
        Countries or group of countries. List of available countries is accessible through get_ycrv_countries().
    maturity: str
        Maturity to get data. By default 10Y.
    change: bool
        Flag to use 1 day change or not. By default False.

    Returns
    -------
    pd.DataFrame
        Spread matrix.


## Getting charts 
### economy.spread(countries: Union[str, List[str]] = 'G7', maturity: str = '10Y', change: bool = False, color: str = 'openbb', raw: bool = False, external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, export: str = '', chart=True)

Display spread matrix. [Source: Investing.com]

    Parameters
    ----------
    countries: Union[str, List[str]]
        Countries or group of countries. List of available countries is accessible through get_ycrv_countries().
    maturity: str
        Maturity to get data. By default 10Y.
    change: bool
        Flag to use 1 day change or not. By default False.
    color: str
        Color theme to use on heatmap, from rgb, binary or openbb By default, openbb.
    raw : bool
        Output only raw data.
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None

