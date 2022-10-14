## Get underlying data 
### stocks.fa.fraud(symbol: str, detail: bool = False) -> pandas.core.frame.DataFrame

Get fraud ratios based on fundamentals

    Parameters
    ----------
    symbol : str
        Stock ticker symbol
    detail : bool
        Whether to provide extra m-score details

    Returns
    -------
    metrics : pd.DataFrame
        The fraud ratios
