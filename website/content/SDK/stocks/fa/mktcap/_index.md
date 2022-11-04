To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### stocks.fa.mktcap(symbol: str, start_date: str = '2019-11-02') -> Tuple[pandas.core.frame.DataFrame, str]

Get market cap over time for ticker. [Source: Yahoo Finance]

    Parameters
    ----------
    symbol: str
        Ticker to get market cap over time
    start_date: str
        Start date to display market cap

    Returns
    -------
    pd.DataFrame:
        Dataframe of estimated market cap over time
    str:
        Currency of ticker

## Getting charts 
### stocks.fa.mktcap(symbol: str, start_date: str = '2019-11-02', export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True)

Display market cap over time. [Source: Yahoo Finance]

    Parameters
    ----------
    symbol: str
        Stock ticker symbol
    start_date: str
        Start date to display market cap
    export: str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
