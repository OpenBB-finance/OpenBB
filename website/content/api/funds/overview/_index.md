To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### funds.overview(country: str = 'united states', limit: int = 20) -> pandas.core.frame.DataFrame



    Parameters
    ----------
    country: str
        Country to get overview for
    limit: int
        Number of results to get

    Returns
    -------
    pd.DataFrame
        Dataframe containing overview

## Getting charts 
### funds.overview(country: str = 'united states', limit: int = 10, export: str = '', chart=True)

Displays an overview of the main funds from a country.

    Parameters
    ----------
    country: str
        Country to get overview for
    limit: int
        Number to show
    export : str
        Format to export data
