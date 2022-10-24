To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### stocks.gov.toplobbying() -> pandas.core.frame.DataFrame

Corporate lobbying details

    Returns
    -------
    pd.DataFrame
        DataFrame of top corporate lobbying


## Getting charts 
### stocks.gov.toplobbying(limit: int = 10, raw: bool = False, export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True)

Top lobbying tickers based on total spent

    Parameters
    ----------
    limit: int
        Number of tickers to show
    raw: bool
        Show raw data
    export:
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None

