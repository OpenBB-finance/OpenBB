To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### crypto.defi.ayr() -> pandas.core.frame.DataFrame

Displays the 30-day history of the Anchor Yield Reserve.
    [Source: https://terra.engineer/]

    Returns
    ----------
    pd.DataFrame
        Dataframe containing historical data

## Getting charts 
### crypto.defi.ayr(export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True) -> None

Displays the 30-day history of the Anchor Yield Reserve.
    [Source: https://terra.engineer/]

    Parameters
    ----------
    export : str
        Export dataframe data to csv,json,xlsx file, by default False
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
