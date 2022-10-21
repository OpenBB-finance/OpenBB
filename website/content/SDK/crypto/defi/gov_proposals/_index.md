To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### crypto.defi.gov_proposals(status: str = '', sortby: str = 'id', ascend: bool = True, limit: int = 10) -> pandas.core.frame.DataFrame

Get terra blockchain governance proposals list [Source: https://fcd.terra.dev/swagger]

    Parameters
    ----------
    status: str
        status of proposal, one from list: ['Voting','Deposit','Passed','Rejected']
    sortby: str
        Key by which to sort data
    ascend: bool
        Flag to sort data ascending
    limit: int
        Number of records to display

    Returns
    -------
    pd.DataFrame
        Terra blockchain governance proposals list

## Getting charts 
### crypto.defi.gov_proposals(limit: int = 10, status: str = 'all', sortby: str = 'id', ascend: bool = True, export: str = '', chart=True) -> None

Display terra blockchain governance proposals list [Source: https://fcd.terra.dev/swagger]

    Parameters
    ----------
    limit: int
        Number of records to display
    status: str
        status of proposal, one from list: ['Voting','Deposit','Passed','Rejected']
    sortby: str
        Key by which to sort data
    ascend: bool
        Flag to sort data ascend
    export : str
        Export dataframe data to csv,json,xlsx file
