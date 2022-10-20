To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### crypto.ov.altindex(period: int = 30, start_date: int = 1262322000, end_date: int = 1666288853) -> pandas.core.frame.DataFrame

Get altcoin index overtime
    [Source: https://blockchaincenter.net]

    Parameters
    ----------
    period: int
       Number of days {30,90,365} to check performance of coins and calculate the altcoin index.
       E.g., 365 checks yearly performance, 90 will check seasonal performance (90 days),
       30 will check monthly performance (30 days).
    start_date : int
        Initial date timestamp (e.g., 1_609_459_200)
    end_date : int
        End date timestamp (e.g., 1_641_588_030)

    Returns
    -------
    pandas.DataFrame:
        Date, Value (Altcoin Index)

## Getting charts 
### crypto.ov.altindex(period: int = 365, start_date: int = 1262322000, end_date: int = 1666288853, export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True) -> None

Displays altcoin index overtime
     [Source: https://blockchaincenter.net]

    Parameters
    ----------
    start_date : int
        Initial date timestamp (e.g., 1_609_459_200)
    end_date : int
        End date timestamp (e.g., 1_641_588_030)
    period: int
        Number of days to check the performance of coins and calculate the altcoin index.
        E.g., 365 will check yearly performance , 90 will check seasonal performance (90 days),
        30 will check monthly performance (30 days).
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
