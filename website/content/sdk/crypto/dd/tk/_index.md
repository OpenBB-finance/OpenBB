To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### crypto.dd.tk(symbol: str, coingecko_id: str) -> Tuple[pandas.core.frame.DataFrame, pandas.core.frame.DataFrame]

Returns coin tokenomics
    [Source: https://messari.io/]

    Parameters
    ----------
    symbol : str
        Crypto symbol to check tokenomics
    coingecko_id : str
        ID from coingecko
    Returns
    -------
    pd.DataFrame
        Metric Value tokenomics
    pd.DataFrame
        Circulating supply overtime

## Getting charts 
### crypto.dd.tk(symbol: str, export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True) -> None

Display coin tokenomics
    [Source: https://messari.io/]

    Parameters
    ----------
    symbol : str
        Crypto symbol to check tokenomics
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (2 axes are expected in the list), by default None
