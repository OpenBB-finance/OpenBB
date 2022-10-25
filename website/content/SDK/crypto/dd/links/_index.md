To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### crypto.dd.links(symbol: str) -> pandas.core.frame.DataFrame

Returns asset's links
    [Source: https://messari.io/]

    Parameters
    ----------
    symbol : str
        Crypto symbol to check links

    Returns
    -------
    pd.DataFrame
        asset links

## Getting charts 
### crypto.dd.links(symbol: str, export: str = '', chart=True) -> None

Display coin links
    [Source: https://messari.io/]

    Parameters
    ----------
    symbol : str
        Crypto symbol to check links
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
