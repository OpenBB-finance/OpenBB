# crypto.defi.ldapps

To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
###crypto.defi.ldapps(num: int = 100) -> pandas.core.frame.DataFrame

Returns information about listed DeFi protocols, their current TVL and changes to it in the last hour/day/week.
    [Source: https://docs.llama.fi/api]

    Parameters
    ----------
    num: int
        The number of dApps to display

    Returns
    -------
    pd.DataFrame
        Information about DeFi protocols

## Getting charts 
###crypto.defi.ldapps(top: int, sortby: str, ascend: bool = False, description: bool = False, export: str = '', chart=True) -> None

Display information about listed DeFi protocols, their current TVL and changes to it in
    the last hour/day/week. [Source: https://docs.llama.fi/api]

    Parameters
    ----------
    top: int
        Number of records to display
    sortby: str
        Key by which to sort data
    ascend: bool
        Flag to sort data descending
    description: bool
        Flag to display description of protocol
    export : str
        Export dataframe data to csv,json,xlsx file
