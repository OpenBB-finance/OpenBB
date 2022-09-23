# crypto.defi.sreturn

To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
###crypto.defi.sreturn(top: int = 200)

Get terra blockchain staking returns history [Source: https://fcd.terra.dev/v1]

    Parameters
    ----------
    top: int
        The number of returns to show

    Returns
    -------
    pd.DataFrame
        historical staking returns

## Getting charts 
###crypto.defi.sreturn(top: int = 90, export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True) -> None

Display terra blockchain staking returns history [Source: https://fcd.terra.dev/swagger]

    Parameters
    ----------
    top: int
        Number of records to display
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None

