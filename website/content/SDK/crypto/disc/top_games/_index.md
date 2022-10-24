To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### crypto.disc.top_games(sortby: str = '', limit: int = 10) -> pandas.core.frame.DataFrame

Get top blockchain games by daily volume and users [Source: https://dappradar.com/]

    Parameters
    ----------
    limit: int
        Number of records to display
    sortby: str
        Key by which to sort data
    Returns
    -------
    pd.DataFrame
        Top blockchain games. Columns: Name, Daily Users, Daily Volume [$]

## Getting charts 
### crypto.disc.top_games(limit: int = 10, export: str = '', sortby: str = '', chart=True) -> None

Displays top blockchain games [Source: https://dappradar.com/]

    Parameters
    ----------
    limit: int
        Number of records to display
    sortby: str
        Key by which to sort data
    export : str
        Export dataframe data to csv,json,xlsx file
