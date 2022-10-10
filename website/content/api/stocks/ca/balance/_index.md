## Get underlying data 
### stocks.ca.balance(similar: List[str], timeframe: str = '2021', quarter: bool = False)

Get balance data. [Source: Marketwatch]

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
