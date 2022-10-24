To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### crypto.dd.gh(symbol: str, dev_activity: bool = False, interval: str = '1d', start_date: str = '2021-10-24T16:10:19Z', end_date: str = '2022-10-24T16:10:19Z') -> pandas.core.frame.DataFrame

Returns  a list of developer activity for a given coin and time interval.

    [Source: https://santiment.net/]

    Parameters
    ----------
    symbol : str
        Crypto symbol to check github activity
    dev_activity: bool
        Whether to filter only for development activity
    start_date : int
        Initial date like string (e.g., 2021-10-01)
    end_date : int
        End date like string (e.g., 2021-10-01)
    interval : str
        Interval frequency (e.g., 1d)

    Returns
    -------
    pd.DataFrame
        developer activity over time

## Getting charts 
### crypto.dd.gh(symbol: str, start_date: str = '2021-10-24T16:10:19Z', dev_activity: bool = False, end_date: str = '2022-10-24T16:10:19Z', interval: str = '1d', export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True) -> None

Returns a list of github activity for a given coin and time interval.

    [Source: https://santiment.net/]

    Parameters
    ----------
    symbol : str
        Crypto symbol to check github activity
    dev_activity: bool
        Whether to filter only for development activity
    start_date : int
        Initial date like string (e.g., 2021-10-01)
    end_date : int
        End date like string (e.g., 2021-10-01)
    interval : str
        Interval frequency (some possible values are: 1h, 1d, 1w)
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
