To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### crypto.disc.top_dapps(sortby: str = '', limit: int = 10) -> pandas.core.frame.DataFrame

Get top decentralized applications by daily volume and users [Source: https://dappradar.com/]

    Parameters
    ----------
    sortby: str
        Key by which to sort data

    Returns
    -------
    pd.DataFrame
        Top decentralized exchanges.
        Columns: Name, Category, Protocols, Daily Users, Daily Volume [$]

## Getting charts 
### crypto.disc.top_dapps(limit: int = 10, export: str = '', sortby: str = '', chart=True) -> None

Displays top decentralized exchanges [Source: https://dappradar.com/]

    Parameters
    ----------
    limit: int
        Number of records to display
    sortby: str
        Key by which to sort data
    export : str
        Export dataframe data to csv,json,xlsx file
