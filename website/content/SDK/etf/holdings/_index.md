To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### etf.holdings(symbol: str) -> pandas.core.frame.DataFrame

Get ETF holdings

    Parameters
    ----------
    symbol: str
        Symbol to get holdings for

    Returns
    -------
    df: pd.DataFrame
        Dataframe of holdings

## Getting charts 
### etf.holdings(symbol: str, limit: int = 10, export: str = '', chart=True)



    Parameters
    ----------
    symbol: str
        ETF symbol to show holdings for
    limit: int
        Number of holdings to show
    export: str
        Format to export data
