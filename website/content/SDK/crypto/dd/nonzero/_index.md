To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### crypto.dd.nonzero(symbol: str, start_date: int = 1262300400, end_date: int = 1666777200) -> pandas.core.frame.DataFrame

Returns addresses with non-zero balance of a certain symbol
    [Source: https://glassnode.com]

    Parameters
    ----------
    symbol : str
        Asset to search (e.g., BTC)
    start_date : int
        Initial date timestamp (e.g., 1_577_836_800)
    end_date : int
        End date timestamp (e.g., 1_609_459_200)

    Returns
    -------
    pd.DataFrame
        addresses with non-zero balances

## Getting charts 
### crypto.dd.nonzero(symbol: str, start_date: int = 1577836800, end_date: int = 1609459200, export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True) -> None

Display addresses with non-zero balance of a certain symbol
    [Source: https://glassnode.org]

    Parameters
    ----------
    symbol : str
        Asset to search (e.g., BTC)
    start_date : int
        Initial date timestamp (e.g., 1_577_836_800)
    end_date : int
        End date timestamp (e.g., 1_609_459_200)
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
