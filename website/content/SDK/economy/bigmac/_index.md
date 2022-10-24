To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### economy.bigmac(country_codes: List[str] = None) -> pandas.core.frame.DataFrame

Display Big Mac Index for given countries

    Parameters
    ----------
    country_codes : List[str]
        List of country codes (ISO-3 letter country code). Codes available through economy.country_codes().

    Returns
    -------
    pd.DataFrame
        Dataframe with Big Mac indices converted to USD equivalent.

## Getting charts 
### economy.bigmac(country_codes: List[str] = None, raw: bool = False, export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True)

Display Big Mac Index for given countries

    Parameters
    ----------
    country_codes : List[str]
        List of country codes (ISO-3 letter country code). Codes available through economy.country_codes().
    raw : bool, optional
        Flag to display raw data, by default False
    export : str, optional
        Format data, by default ""
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
