To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### crypto.ov.cpcontracts(platform_id: str = 'eth-ethereum', sortby: str = 'active', ascend: bool = True) -> pandas.core.frame.DataFrame

Gets all contract addresses for given platform [Source: CoinPaprika]
    Parameters
    ----------
    platform_id: str
        Blockchain platform like eth-ethereum
    sortby: str
        Key by which to sort data
    ascend: bool
        Flag to sort data ascend

    Returns
    -------
    pandas.DataFrame
         id, type, active

## Getting charts 
### crypto.ov.cpcontracts(symbol: str, sortby: str = 'active', ascend: bool = True, limit: int = 15, export: str = '', chart=True) -> None

Gets all contract addresses for given platform. [Source: CoinPaprika]

    Parameters
    ----------
    platform: str
        Blockchain platform like eth-ethereum
    limit: int
        Number of records to display
    sortby: str
        Key by which to sort data
    ascend: bool
        Flag to sort data ascending
    export : str
        Export dataframe data to csv,json,xlsx file
