To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### stocks.ins.act(symbol: str) -> pandas.core.frame.DataFrame

Get insider activity. [Source: Business Insider]

    Parameters
    ----------
    symbol : str
        Ticker symbol to get insider activity data from

    Returns
    -------
    df_insider : pd.DataFrame
        Get insider activity data

## Getting charts 
### stocks.ins.act(data: pandas.core.frame.DataFrame, symbol: str, start_date: str = '2019-10-31', interval: str = '1440min', limit: int = 10, raw: bool = False, export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True)

Display insider activity. [Source: Business Insider]

    Parameters
    ----------
    data: pd.DataFrame
        Stock dataframe
    symbol: str
        Due diligence ticker symbol
    start_date: str
        Start date of the stock data
    interval: str
        Stock data interval
    limit: int
        Number of latest days of inside activity
    raw: bool
        Print to console
    export: str
        Export dataframe data to csv,json,xlsx file
    external_axes: Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
