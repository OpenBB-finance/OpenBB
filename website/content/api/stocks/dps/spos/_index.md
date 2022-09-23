To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### stocks.dps.spos(symbol: str) -> pandas.core.frame.DataFrame

Get net short position. [Source: Stockgrid]

    Parameters
    ----------
    symbol: str
        Stock to get data from

    Returns
    ----------
    pd.DataFrame
        Net short position

## Getting charts 
### stocks.dps.spos(symbol: str, limit: int = 84, raw: bool = False, export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True)

Plot net short position. [Source: Stockgrid]

    Parameters
    ----------
    symbol: str
        Stock to plot for
    limit : int
        Number of last open market days to show
    raw : bool
        Flag to print raw data instead
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (2 axes are expected in the list), by default None

