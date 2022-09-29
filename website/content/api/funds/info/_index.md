To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### funds.info(name: str, country: str = 'united states') -> pandas.core.frame.DataFrame



    Parameters
    ----------
    name: str
        Name of fund (not symbol) to get information
    country: str
        Country of fund

    Returns
    -------
    pd.DataFrame
        Dataframe of fund information

## Getting charts 
### funds.info(name: str, country: str = 'united states', chart=True)

Display fund information.  Finds name from symbol first if name is false

    Parameters
    ----------
    name: str
        Fund name to get info for
    country : str
        Country of fund
