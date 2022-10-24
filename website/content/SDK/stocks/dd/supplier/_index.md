## Get underlying data 
### stocks.dd.supplier(symbol: str, limit: int = 50) -> pandas.core.frame.DataFrame

Get suppliers from ticker provided. [Source: CSIMarket]

    Parameters
    ----------
    symbol: str
        Ticker to select suppliers from
    limit: int
        The maximum number of rows to show

    Returns
    -------
    pd.DataFrame
        A dataframe of suppliers
