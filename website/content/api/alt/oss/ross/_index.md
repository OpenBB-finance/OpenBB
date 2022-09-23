To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### alt.oss.ross() -> pandas.core.frame.DataFrame

Get startups from ROSS index [Source: https://runacap.com/]

    Parameters
    ----------

    Returns
    -------
    pandas.DataFrame:
        list of startups

## Getting charts 
### alt.oss.ross(limit: int = 10, sortby: str = 'Stars AGR [%]', ascend: bool = False, show_chart: bool = False, show_growth: bool = True, chart_type: str = 'stars', export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True) -> None

Display list of startups from ross index [Source: https://runacap.com/]

    Parameters
    ----------
    limit: int
        Number of startups to search
    sortby: str
        Key by which to sort data. Default: Stars AGR [%]
    ascend: bool
        Flag to sort data descending
    show_chart: bool
        Flag to show chart with startups
    show_growth: bool
        Flag to show growth line chart
    chart_type: str
        Chart type {stars,forks}
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
