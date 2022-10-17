To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### stocks.ca.income(similar: List[str], timeframe: str = '2021', quarter: bool = False)

Get income data. [Source: Marketwatch]

    Parameters
    ----------
    similar : List[str]
        List of tickers to compare.
        Comparable companies can be accessed through
        finnhub_peers(), finviz_peers(), polygon_peers().
    timeframe : str
        Column header to compare
    quarter : bool, optional
        Whether to use quarterly statements, by default False
    export : str, optional
        Format to export data

## Getting charts 
### stocks.ca.income(symbols: List[str], timeframe: str = '2021', quarter: bool = False, export: str = '', chart=True)

Display income data. [Source: Marketwatch]

    Parameters
    ----------
    symbols : List[str]
        List of tickers to compare. Enter tickers you want to see as shown below:
        ["TSLA", "AAPL", "NFLX", "BBY"]
        You can also get a list of comparable peers with
        finnhub_peers(), finviz_peers(), polygon_peers().
    timeframe : str
        What year to look at
    quarter : bool, optional
        Whether to use quarterly statements, by default False
    export : str, optional
        Format to export data
