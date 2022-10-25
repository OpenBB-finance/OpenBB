## Get underlying data 
### stocks.fa.shrs(symbol: str, holder: str = 'institutional') -> pandas.core.frame.DataFrame

Get shareholders from yahoo

    Parameters
    ----------
    symbol : str
        Stock ticker symbol
    holder : str
        Which holder to get table for

    Returns
    -------
    pd.DataFrame
        Major holders
