To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### crypto.defi.stvl() -> pandas.core.frame.DataFrame

Returns historical values of the total sum of TVLs from all listed protocols.
    [Source: https://docs.llama.fi/api]

    Returns
    -------
    pd.DataFrame
        Historical values of total sum of Total Value Locked from all listed protocols.

## Getting charts 
### crypto.defi.stvl(limit: int = 5, export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True) -> None

Displays historical values of the total sum of TVLs from all listed protocols.
    [Source: https://docs.llama.fi/api]

    Parameters
    ----------
    limit: int
        Number of records to display, by default 5
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
