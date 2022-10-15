To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### stocks.ba.messages(symbol: str, limit: int = 30) -> pandas.core.frame.DataFrame

Get last messages for a given ticker [Source: stocktwits]

    Parameters
    ----------
    symbol : str
        Stock ticker symbol
    limit : int
        Number of messages to get

    Returns
    -------
    pd.DataFrame
        Dataframe of messages

## Getting charts 
### stocks.ba.messages(symbol: str, limit: int = 30, chart=True)

Print up to 30 of the last messages on the board. [Source: Stocktwits]

    Parameters
    ----------
    symbol: str
        Stock ticker symbol
    limit: int
        Number of messages to get
