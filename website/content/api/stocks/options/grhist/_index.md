To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### stocks.options.grhist(symbol: str, expiry: str, strike: float, chain_id: str = '', put: bool = False) -> pandas.core.frame.DataFrame

Get histoical option greeks

    Parameters
    ----------
    symbol: str
        Stock ticker symbol
    expiry: str
        Option expiration date
    strike: float
        Strike price to look for
    chain_id: str
        OCC option symbol.  Overwrites other inputs
    put: bool
        Is this a put option?

    Returns
    -------
    df: pd.DataFrame
        Dataframe containing historical greeks

## Getting charts 
### stocks.options.grhist(symbol: str, expiry: str, strike: float, greek: str = 'Delta', chain_id: str = '', put: bool = False, raw: bool = False, limit: int = 20, export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True)

Plots historical greeks for a given option. [Source: Syncretism]

    Parameters
    ----------
    symbol: str
        Stock ticker
    expiry: str
        Expiration date
    strike: float
        Strike price to consider
    greek: str
        Greek variable to plot
    chain_id: str
        OCC option chain.  Overwrites other variables
    put: bool
        Is this a put option?
    raw: bool
        Print to console
    limit: int
        Number of rows to show in raw
    export: str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
