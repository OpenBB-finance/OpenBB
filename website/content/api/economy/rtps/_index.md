To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### economy.rtps() -> pandas.core.frame.DataFrame

Get real-time performance sector data

    Returns
    ----------
    df_sectors : pd.Dataframe
        Real-time performance data

## Getting charts 
### economy.rtps(raw: bool = False, export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True)

Display Real-Time Performance sector. [Source: AlphaVantage]

    Parameters
    ----------
    raw : bool
        Output only raw data
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
