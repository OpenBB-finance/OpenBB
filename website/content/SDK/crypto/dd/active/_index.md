To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### crypto.dd.active(symbol: str, interval: str = '24h', start_date: int = 1262300400, end_date: int = 1666620619) -> pandas.core.frame.DataFrame

Returns active addresses of a certain symbol
    [Source: https://glassnode.com]

    Parameters
    ----------
    symbol : str
        Asset to search active addresses (e.g., BTC)
    start_date : int
        Initial date timestamp (e.g., 1_614_556_800)
    end_date : int
        End date timestamp (e.g., 1_614_556_800)
    interval : str
        Interval frequency (e.g., 24h)

    Returns
    -------
    pd.DataFrame
        active addresses over time

## Getting charts 
### crypto.dd.active(symbol: str, start_date: int = 1577836800, end_date: int = 1609459200, interval: str = '24h', export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True) -> None

Display active addresses of a certain symbol over time
    [Source: https://glassnode.org]

    Parameters
    ----------
    symbol : str
        Asset to search active addresses (e.g., BTC)
    start_date : int
        Initial date timestamp (e.g., 1_614_556_800)
    end_date : int
        End date timestamp (e.g., 1_614_556_800)
    interval : str
        Interval frequency (possible values are: 24h, 1w, 1month)
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
