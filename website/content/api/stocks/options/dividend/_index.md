## Get underlying data 
### stocks.options.dividend(symbol: str) -> pandas.core.series.Series

Gets option chain from yf for given ticker and expiration

    Parameters
    ----------
    symbol: str
        Ticker symbol to get options for

    Returns
    -------
    chains: yf.ticker.Dividends
        Dividends
