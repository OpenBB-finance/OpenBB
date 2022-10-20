To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### economy.ycrv(country: str = 'United States') -> pandas.core.frame.DataFrame

Get yield curve for specified country. [Source: Investing.com]

    Parameters
    ----------
    country: str
        Country to display yield curve. List of available countries is accessible through get_ycrv_countries().

    Returns
    -------
    pd.DataFrame
        Country yield curve

## Getting charts 
### economy.ycrv(country: str = 'United States', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, raw: bool = False, export: str = '', chart=True)

Display yield curve for specified country. [Source: Investing.com]

    Parameters
    ----------
    country: str
        Country to display yield curve. List of available countries is accessible through get_ycrv_countries().
    export : str
        Export dataframe data to csv,json,xlsx file
