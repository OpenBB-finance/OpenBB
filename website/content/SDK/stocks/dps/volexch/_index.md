To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### stocks.dps.volexch(symbol: str) -> pandas.core.frame.DataFrame

Gets short data for 5 exchanges [https://ftp.nyse.com] starting at 1/1/2021

    Parameters
    ----------
    symbol : str
        Ticker to get data for

    Returns
    -------
    pd.DataFrame
        DataFrame of short data by exchange

## Getting charts 
### stocks.dps.volexch(symbol: str, raw: bool = False, sortby: str = '', ascend: bool = False, mpl: bool = True, export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True)

Display short data by exchange

    Parameters
    ----------
    symbol : str
        Stock ticker
    raw : bool
        Flag to display raw data
    sortby: str
        Column to sort by
    ascend: bool
        Sort in ascending order
    mpl: bool
        Display using matplotlib
    export : str, optional
        Format  of export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None

