To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### crypto.defi.sinfo(address: str = '') -> Tuple[pandas.core.frame.DataFrame, str]

Get staking info for provided terra account [Source: https://fcd.terra.dev/swagger]

    Parameters
    ----------
    address: str
        terra blockchain address e.g. terra1jvwelvs7rdk6j3mqdztq5tya99w8lxk6l9hcqg
    Returns
    -------
    Tuple[pd.DataFrame, str]:
        luna delegations and summary report for given address

## Getting charts 
### crypto.defi.sinfo(address: str = '', limit: int = 10, export: str = '', chart=True) -> None

Display staking info for provided terra account address [Source: https://fcd.terra.dev/swagger]

    Parameters
    ----------
    address: str
        terra blockchain address e.g. terra1jvwelvs7rdk6j3mqdztq5tya99w8lxk6l9hcqg
    limit: int
        Number of records to display
    export : str
        Export dataframe data to csv,json,xlsx file
