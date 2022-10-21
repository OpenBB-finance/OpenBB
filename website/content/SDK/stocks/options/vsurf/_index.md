To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### stocks.options.vsurf(symbol: str) -> pandas.core.frame.DataFrame

Gets IV surface for calls and puts for ticker

    Parameters
    ----------
    symbol: str
        Stock ticker symbol to get

    Returns
    -------
    pd.DataFrame
        Dataframe of DTE, Strike and IV

## Getting charts 
### stocks.options.vsurf(symbol: str, export: str = '', z: str = 'IV', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True)

Display vol surface

    Parameters
    ----------
    symbol : str
        Ticker symbol to get surface for
    export : str
        Format to export data
    z : str
        The variable for the Z axis
    external_axes: Optional[List[plt.Axes]]
        External axes (1 axis is expected in the list), by default None
