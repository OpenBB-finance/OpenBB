To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### crypto.defi.gdapps(limit: int = 50) -> pandas.core.frame.DataFrame

Display top dApps (in terms of TVL) grouped by chain.
    [Source: https://docs.llama.fi/api]

    Parameters
    ----------
    limit: int
        Number of top dApps to display

    Returns
    -------
    pd.DataFrame
        Information about DeFi protocols grouped by chain

## Getting charts 
### crypto.defi.gdapps(limit: int = 50, export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True) -> None

Display top dApps (in terms of TVL) grouped by chain.
    [Source: https://docs.llama.fi/api]

    Parameters
    ----------
    num: int
        Number of top dApps to display
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
