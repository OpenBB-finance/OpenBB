To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### crypto.defi.ldapps(limit: int = 100) -> pandas.core.frame.DataFrame

Returns information about listed DeFi protocols, their current TVL and changes to it in the last hour/day/week.
    [Source: https://docs.llama.fi/api]

    Parameters
    ----------
    limit: int
        The number of dApps to display

    Returns
    -------
    pd.DataFrame
        Information about DeFi protocols

## Getting charts 
### crypto.defi.ldapps(limit: int, sortby: str, ascend: bool = False, description: bool = False, export: str = '', chart=True) -> None

Display information about listed DeFi protocols, their current TVL and changes to it in
    the last hour/day/week. [Source: https://docs.llama.fi/api]

    Parameters
    ----------
    limit: int
        Number of records to display
    sortby: str
        Key by which to sort data
    ascend: bool
        Flag to sort data descending
    description: bool
        Flag to display description of protocol
    export : str
        Export dataframe data to csv,json,xlsx file
