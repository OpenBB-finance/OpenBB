To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### stocks.options.chains_yf(symbol: str, expiry: str, min_sp: float = -1, max_sp: float = -1, calls: bool = True, puts: bool = True) -> pandas.core.frame.DataFrame

Get full option chains with calculated greeks

    Parameters
    ----------
    symbol: str
        Stock ticker symbol
    expiry: str
        Expiration date for chain in format YYY-mm-dd
    calls: bool
        Flag to get calls
    puts: bool
        Flag to get puts

    Returns
    -------
    pd.DataFrame
        DataFrame of option chain.  If both calls and puts

## Getting charts 
### stocks.options.chains_yf(symbol: str, expiry: str, min_sp: float = -1, max_sp: float = -1, calls_only: bool = False, puts_only: bool = False, export: str = '', chart=True)

Display option chains for given ticker and expiration

    Parameters
    ----------
    symbol: str
        Stock ticker symbol
    expiry: str
        Expiration for option chain
    min_sp: float
        Min strike
    max_sp: float
        Max strike
    calls_only: bool
        Flag to get calls only
    puts_only: bool
        Flag to get puts only
    export: str
        Format to export data

