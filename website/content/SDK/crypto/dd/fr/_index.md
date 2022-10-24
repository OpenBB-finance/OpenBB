To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### crypto.dd.fr(symbol: str) -> Tuple[str, pandas.core.frame.DataFrame, pandas.core.frame.DataFrame, pandas.core.frame.DataFrame]

Returns coin fundraising
    [Source: https://messari.io/]

    Parameters
    ----------
    symbol : str
        Crypto symbol to check fundraising

    Returns
    -------
    str
        launch summary
    pd.DataFrame
        Sales rounds
    pd.DataFrame
        Treasury Accounts
    pd.DataFrame
        Metric Value launch details

## Getting charts 
### crypto.dd.fr(symbol: str, export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True) -> None

Display coin fundraising
    [Source: https://messari.io/]

    Parameters
    ----------
    symbol : str
        Crypto symbol to check coin fundraising
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
