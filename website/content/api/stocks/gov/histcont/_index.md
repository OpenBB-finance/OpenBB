To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### stocks.gov.histcont(symbol: str) -> pandas.core.frame.DataFrame

Get historical quarterly government contracts [Source: quiverquant.com]

    Parameters
    ----------
    symbol: str
        Ticker symbol to get congress trading data from

    Returns
    -------
    pd.DataFrame
        Historical quarterly government contracts

## Getting charts 
### stocks.gov.histcont(symbol: str, raw: bool = False, export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True)

Show historical quarterly government contracts [Source: quiverquant.com]

    Parameters
    ----------
    symbol: str
        Ticker symbol to get congress trading data from
    raw: bool
        Flag to display raw data
    export: str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
