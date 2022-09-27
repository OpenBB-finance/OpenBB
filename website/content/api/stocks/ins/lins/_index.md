To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### stocks.ins.lins(symbol: str) -> pandas.core.frame.DataFrame

Get last insider activity for a given stock ticker. [Source: Finviz]

    Parameters
    ----------
    symbol : str
        Stock ticker symbol

    pd.DataFrame
        Latest insider trading activity

## Getting charts 
### stocks.ins.lins(symbol: str, limit: int = 10, export: str = '', chart=True)

Display insider activity for a given stock ticker. [Source: Finviz]

    Parameters
    ----------
    symbol : str
        Stock ticker symbol
    limit : int
        Number of latest insider activity to display
    export : str
        Export dataframe data to csv,json,xlsx file
