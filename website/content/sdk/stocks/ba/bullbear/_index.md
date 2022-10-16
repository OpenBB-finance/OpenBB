To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### stocks.ba.bullbear(symbol: str) -> Tuple[int, int, int, int]

Gets bullbear sentiment for ticker [Source: stocktwits]

    Parameters
    ----------
    symbol : str
        Ticker symbol to look at

    Returns
    -------
    int
        Watchlist count
    int
        Number of cases found for ticker
    int
        Number of bullish statements
    int
        Number of bearish statements

## Getting charts 
### stocks.ba.bullbear(symbol: str, chart=True)


    Print bullbear sentiment based on last 30 messages on the board.
    Also prints the watchlist_count. [Source: Stocktwits]

    Parameters
    ----------
    symbol: str
        Stock ticker symbol
