To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### crypto.defi.dpi(sortby: str = 'TVL_$', ascend: bool = False) -> pandas.core.frame.DataFrame

Scrapes data from DeFi Pulse with all DeFi Pulse crypto protocols.
    [Source: https://defipulse.com/]

    Returns
    -------
    pd.DataFrame
        List of DeFi Pulse protocols.

## Getting charts 
### crypto.defi.dpi(limit: int = 10, sortby: str = 'TVL_$', ascend: bool = False, export: str = '', chart=True) -> None

Displays all DeFi Pulse crypto protocols.
    [Source: https://defipulse.com/]

    Parameters
    ----------
    limit: int
        Number of records to display
    sortby: str
        Key by which to sort data (Possible values are: "Rank", "Name", "Chain", "Sector",
        "30D_Users", "TVL_$", "1_Day_%"), by default TVL
    ascend: bool
        Flag to sort data ascending, by default False
    export : str
        Export dataframe data to csv,json,xlsx file, by default False
