## Get underlying data 
### stocks.ba.queries(symbol: str, limit: int = 10) -> pandas.core.frame.DataFrame

Get related queries from google api [Source: google]

    Parameters
    ----------
    symbol: str
        Stock ticker symbol to compare
    limit: int
        Number of queries to show

    Returns
    -------
    dict : {'top': pd.DataFrame or None, 'rising': pd.DataFrame or None}

