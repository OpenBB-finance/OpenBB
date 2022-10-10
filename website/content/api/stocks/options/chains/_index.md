To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### stocks.options.chains(symbol: str, expiry: str) -> pandas.core.frame.DataFrame

Display option chains [Source: Tradier]"

    Parameters
    ----------
    symbol : str
        Ticker to get options for
    expiry : str
        Expiration date in the form of "YYYY-MM-DD"

    Returns
    -------
    chains: pd.DataFrame
        Dataframe with options for the given Symbol and Expiration date

## Getting charts 
### stocks.options.chains(symbol: str, expiry: str, to_display: List[str] = None, min_sp: float = -1, max_sp: float = -1, calls_only: bool = False, puts_only: bool = False, export: str = '', chart=True)

Display option chain

    Parameters
    ----------
    symbol: str
        Stock ticker symbol
    expiry: str
        Expiration date of option
    to_display: List[str]
        List of columns to display
    min_sp: float
        Min strike price to display
    max_sp: float
        Max strike price to display
    calls_only: bool
        Only display calls
    puts_only: bool
        Only display puts
    export: str
        Format to  export file
