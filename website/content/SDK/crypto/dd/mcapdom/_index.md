To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### crypto.dd.mcapdom(symbol: str, interval: str = '1d', start_date: str = '2021-10-24', end_date: str = '2022-10-24') -> pandas.core.frame.DataFrame

Returns market dominance of a coin over time
    [Source: https://messari.io/]

    Parameters
    ----------
    symbol : str
        Crypto symbol to check market cap dominance
    interval : str
        Interval frequency (possible values are: 5m, 15m, 30m, 1h, 1d, 1w)
    start_date : int
        Initial date like string (e.g., 2021-10-01)
    end_date : int
        End date like string (e.g., 2021-10-01)

    Returns
    -------
    pd.DataFrame
        market dominance percentage over time

## Getting charts 
### crypto.dd.mcapdom(symbol: str, start_date: str = '2021-10-24', end_date: str = '2022-10-24', interval: str = '1d', export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True) -> None

Display market dominance of a coin over time
    [Source: https://messari.io/]

    Parameters
    ----------
    symbol : str
        Crypto symbol to check market cap dominance
    start_date : int
        Initial date like string (e.g., 2021-10-01)
    end_date : int
        End date like string (e.g., 2021-10-01)
    interval : str
        Interval frequency (possible values are: 5m, 15m, 30m, 1h, 1d, 1w)
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
