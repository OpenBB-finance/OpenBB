## Get underlying data 
### stocks.options.option_chain(symbol: str, expiry: str)

Gets option chain from yf for given ticker and expiration

    Parameters
    ----------
    symbol: str
        Ticker symbol to get options for
    expiry: str
        Date to get options for. YYYY-MM-DD

    Returns
    -------
    chains: yf.ticker.Options
        Options chain
