To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### stocks.fa.splits(symbol: str) -> pandas.core.frame.DataFrame

Get splits and reverse splits events. [Source: Yahoo Finance]

    Parameters
    ----------
    symbol: str
        Ticker to get forward and reverse splits

    Returns
    -------
    pd.DataFrame:
        Dataframe of forward and reverse splits

## Getting charts 
### stocks.fa.splits(symbol: str, export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True)

Display splits and reverse splits events. [Source: Yahoo Finance]

    Parameters
    ----------
    symbol: str
        Stock ticker symbol
    export: str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
