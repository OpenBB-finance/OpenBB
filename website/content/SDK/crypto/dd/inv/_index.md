To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### crypto.dd.inv(symbol: str) -> Tuple[pandas.core.frame.DataFrame, pandas.core.frame.DataFrame]

Returns coin investors
    [Source: https://messari.io/]

    Parameters
    ----------
    symbol : str
        Crypto symbol to check investors

    Returns
    -------
    pd.DataFrame
        individuals
    pd.DataFrame
        organizations

## Getting charts 
### crypto.dd.inv(symbol: str, export: str = '', chart=True) -> None

Display coin investors
    [Source: https://messari.io/]

    Parameters
    ----------
    symbol : str
        Crypto symbol to check coin investors
    export : str
        Export dataframe data to csv,json,xlsx file
