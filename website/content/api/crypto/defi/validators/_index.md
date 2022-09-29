To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### crypto.defi.validators(sortby: str = 'votingPower', ascend: bool = True) -> pandas.core.frame.DataFrame

Get information about terra validators [Source: https://fcd.terra.dev/swagger]

    Parameters
    -----------
    sortby: str
        Key by which to sort data. Choose from:
        validatorName, tokensAmount, votingPower, commissionRate, status, uptime
    ascend: bool
        Flag to sort data descending

    Returns
    -------
    pd.DataFrame
        terra validators details

## Getting charts 
### crypto.defi.validators(limit: int = 10, sortby: str = 'votingPower', ascend: bool = True, export: str = '', chart=True) -> None

Display information about terra validators [Source: https://fcd.terra.dev/swagger]

    Parameters
    ----------
    limit: int
        Number of records to display
    sortby: str
        Key by which to sort data. Choose from:
        validatorName, tokensAmount, votingPower, commissionRate, status, uptime
    ascend: bool
        Flag to sort data descending
    export : str
        Export dataframe data to csv,json,xlsx file
