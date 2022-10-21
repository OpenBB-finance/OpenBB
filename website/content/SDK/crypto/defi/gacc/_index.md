To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### crypto.defi.gacc(cumulative: bool = True) -> pandas.core.frame.DataFrame

Get terra blockchain account growth history [Source: https://fcd.terra.dev/swagger]

    Parameters
    ----------
    cumulative: bool
        distinguish between periodical and cumulative account growth data
    Returns
    -------
    pd.DataFrame
        historical data of accounts growth

## Getting charts 
### crypto.defi.gacc(kind: str = 'total', cumulative: bool = False, limit: int = 90, export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True) -> None

Display terra blockchain account growth history [Source: https://fcd.terra.dev/swagger]

    Parameters
    ----------
    limit: int
        Number of records to display
    kind: str
        display total account count or active account count. One from list [active, total]
    cumulative: bool
        Flag to show cumulative or discrete values. For active accounts only discrete value are available.
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
