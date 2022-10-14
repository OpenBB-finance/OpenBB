To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### crypto.defi.sratio(limit: int = 200)

Get terra blockchain staking ratio history [Source: https://fcd.terra.dev/swagger]

    Parameters
    ----------
    limit: int
        The number of ratios to show

    Returns
    -------
    pd.DataFrame
        historical staking ratio

## Getting charts 
### crypto.defi.sratio(limit: int = 90, export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True) -> None

Display terra blockchain staking ratio history [Source: https://fcd.terra.dev/v1]

    Parameters
    ----------
    limit: int
        Number of records to display
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
