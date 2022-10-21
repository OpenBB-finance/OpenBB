## Get underlying data 
### stocks.tob(symbol: str, exchange: str = 'BZX') -> Tuple[pandas.core.frame.DataFrame, pandas.core.frame.DataFrame]

Get top of book bid and ask for ticker on exchange [CBOE.com]

    Parameters
    ----------
    symbol: str
        Ticker to get
    exchange: str
        Exchange to look at.  Can be `BZX`,`EDGX`, `BYX`, `EDGA`

    Returns
    -------
    pd.DatatFrame
        Dataframe of Bids
    pd.DataFrame
        Dataframe of asks

