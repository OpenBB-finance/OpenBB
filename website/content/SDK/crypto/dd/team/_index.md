To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### crypto.dd.team(symbol: str) -> Tuple[pandas.core.frame.DataFrame, pandas.core.frame.DataFrame]

Returns coin team
    [Source: https://messari.io/]

    Parameters
    ----------
    symbol : str
        Crypto symbol to check team

    Returns
    -------
    pd.DataFrame
        individuals
    pd.DataFrame
        organizations

## Getting charts 
### crypto.dd.team(symbol: str, export: str = '', chart=True) -> None

Display coin team
    [Source: https://messari.io/]

    Parameters
    ----------
    symbol : str
        Crypto symbol to check coin team
    export : str
        Export dataframe data to csv,json,xlsx file
