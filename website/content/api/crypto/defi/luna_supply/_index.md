To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### crypto.defi.luna_supply(supply_type: str = 'lunaSupplyChallengeStats', days: int = 30) -> pandas.core.frame.DataFrame

Get supply history of the Terra ecosystem

    Source: [Smartstake.io]

    Parameters
    ----------
    supply_type: str
        Supply type to unpack json
    days: int
        Day count to fetch data

    Returns
    -------
    pd.DataFrame
        Dataframe of supply history data

## Getting charts 
### crypto.defi.luna_supply(days: int = 30, export: str = '', supply_type: str = 'lunaSupplyChallengeStats', limit: int = 5, external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True)

Display Luna circulating supply stats

    Parameters
    ----------
    days: int
        Number of days
    supply_type: str
        Supply type to unpack json
    export: str
        Export type
    limit: int
        Number of results display on the terminal
        Default: 5
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    Returns
        None
    -------
