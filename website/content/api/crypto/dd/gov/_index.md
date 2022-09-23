To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### crypto.dd.gov(symbol: str) -> Tuple[str, pandas.core.frame.DataFrame]

Returns coin governance
    [Source: https://messari.io/]

    Parameters
    ----------
    symbol : str
        Crypto symbol to check governance

    Returns
    -------
    str
        governance summary
    pd.DataFrame
        Metric Value with governance details

## Getting charts 
### crypto.dd.gov(symbol: str, export: str = '', chart=True) -> None

Display coin governance
    [Source: https://messari.io/]

    Parameters
    ----------
    symbol : str
        Crypto symbol to check coin governance
    export : str
        Export dataframe data to csv,json,xlsx file
