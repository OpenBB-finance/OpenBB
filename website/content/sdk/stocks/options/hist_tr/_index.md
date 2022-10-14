To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### stocks.options.hist_tr(symbol: str, expiry: str, strike: float = 0, put: bool = False, chain_id: Optional[str] = None) -> pandas.core.frame.DataFrame


    Gets historical option pricing.  This inputs either ticker, expiration, strike or the OCC chain ID and processes
    the request to tradier for historical premiums.

    Parameters
    ----------
    symbol: str
        Stock ticker symbol
    expiry: str
        Option expiration date
    strike: int
        Option strike price
    put: bool
        Is this a put option?
    chain_id: Optional[str]
        OCC chain ID

    Returns
    -------
    df_hist: pd.DataFrame
        Dataframe of historical option prices

## Getting charts 
### stocks.options.hist_tr(symbol: str, expiry: str, strike: float = 0, put: bool = False, raw: bool = False, chain_id: str = None, export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True)

Plot historical option prices

    Parameters
    ----------
    symbol: str
        Stock ticker symbol
    expiry: str
        Expiry date of option
    strike: float
        Option strike price
    put: bool
        Is this a put option?
    raw: bool
        Print raw data
    chain_id: str
        OCC option symbol
    export: str
        Format of export file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
