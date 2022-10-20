To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### stocks.dd.pt(symbol: str) -> pandas.core.frame.DataFrame

Get analysts' price targets for a given stock. [Source: Business Insider]

    Parameters
    ----------
    symbol : str
        Ticker symbol

    Returns
    -------
    pd.DataFrame
        Analysts data

## Getting charts 
### stocks.dd.pt(symbol: str, data: pandas.core.frame.DataFrame, start_date: str = '2022-10-18', limit: int = 10, raw: bool = False, export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True)

Display analysts' price targets for a given stock. [Source: Business Insider]

    Parameters
    ----------
    symbol: str
        Due diligence ticker symbol
    data: DataFrame
        Due diligence stock dataframe
    start_date : str
        Start date of the stock data
    limit : int
        Number of latest price targets from analysts to print
    raw: bool
        Display raw data only
    export: str
        Export dataframe data to csv,json,xlsx file
    external_axes: Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
