To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### crypto.dd.pi(symbol: str) -> Tuple[pandas.core.frame.DataFrame, pandas.core.frame.DataFrame, pandas.core.frame.DataFrame, pandas.core.frame.DataFrame]

Returns coin product info
    [Source: https://messari.io/]

    Parameters
    ----------
    symbol : str
        Crypto symbol to check product info

    Returns
    -------
    pd.DataFrame
        Metric, Value with project and technology details
    pd.DataFrame
        coin public repos
    pd.DataFrame
        coin audits
    pd.DataFrame
        coin known exploits/vulns

## Getting charts 
### crypto.dd.pi(symbol: str, export: str = '', chart=True) -> None

Display project info
    [Source: https://messari.io/]

    Parameters
    ----------
    symbol : str
        Crypto symbol to check project info
    export : str
        Export dataframe data to csv,json,xlsx file
