To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### crypto.defi.sreturn(limit: int = 200)

Get terra blockchain staking returns history [Source: https://fcd.terra.dev/v1]

    Parameters
    ----------
    limit: int
        The number of returns to show

    Returns
    -------
    pd.DataFrame
        historical staking returns

## Getting charts 
### crypto.defi.sreturn(limit: int = 90, export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True) -> None

Display terra blockchain staking returns history [Source: https://fcd.terra.dev/swagger]

    Parameters
    ----------
    limit: int
        Number of records to display
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None

