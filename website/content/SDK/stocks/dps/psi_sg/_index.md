To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### stocks.dps.psi_sg(symbol: str) -> Tuple[pandas.core.frame.DataFrame, List]

Get price vs short interest volume. [Source: Stockgrid]

    Parameters
    ----------
    symbol : str
        Stock to get data from

    Returns
    ----------
    pd.DataFrame
        Short interest volume data
    List
        Price data

## Getting charts 
### stocks.dps.psi_sg(symbol: str, limit: int = 84, raw: bool = False, export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True)

Plot price vs short interest volume. [Source: Stockgrid]

    Parameters
    ----------
    symbol : str
        Stock to plot for
    limit : int
        Number of last open market days to show
    raw : bool
        Flag to print raw data instead
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (3 axes are expected in the list), by default None

