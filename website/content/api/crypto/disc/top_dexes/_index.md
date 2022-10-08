To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### crypto.disc.top_dexes(sortby: str = '', limit: int = 10) -> pandas.core.frame.DataFrame

Get top dexes by daily volume and users [Source: https://dappradar.com/]

    Parameters
    ----------
    sortby: str
        Key by which to sort data

    Returns
    -------
    pd.DataFrame
        Top decentralized exchanges. Columns: Name, Daily Users, Daily Volume [$]

## Getting charts 
### crypto.disc.top_dexes(limit: int = 10, export: str = '', sortby: str = '', chart=True) -> None

Displays top decentralized exchanges [Source: https://dappradar.com/]

    Parameters
    ----------
    limit: int
        Number of records to display
    sortby: str
        Key by which to sort data
    export : str
        Export dataframe data to csv,json,xlsx file
