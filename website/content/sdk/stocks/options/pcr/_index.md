To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### stocks.options.pcr(symbol: str, window: int = 30, start_date: str = '2021-10-19') -> pandas.core.frame.DataFrame

Gets put call ratio over last time window [Source: AlphaQuery.com]

    Parameters
    ----------
    symbol: str
        Ticker symbol to look for
    window: int, optional
        Window to consider, by default 30
    start_date: str, optional
        Start date to plot, by default last 366 days

## Getting charts 
### stocks.options.pcr(symbol: str, window: int = 30, start_date: str = '2021-10-19', export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True)

Display put call ratio [Source: AlphaQuery.com]

    Parameters
    ----------
    symbol : str
        Stock ticker symbol
    window : int, optional
        Window length to look at, by default 30
    start_date : str, optional
        Starting date for data, by default (datetime.now() - timedelta(days=366)).strftime("%Y-%m-%d")
    export : str, optional
        Format to export data, by default ""
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
