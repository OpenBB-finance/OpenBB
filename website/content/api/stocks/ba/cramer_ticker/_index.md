To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### stocks.ba.cramer_ticker(symbol: str) -> pandas.core.frame.DataFrame

Get cramer recommendations from beginning of year for given ticker

    Parameters
    ----------
    symbol: str
        Ticker to get recommendations for

    Returns
    -------
    pd.DataFrame:
        Dataframe with dates and recommendations

## Getting charts 
### stocks.ba.cramer_ticker(symbol: str, raw: bool = False, export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True)

Display ticker close with Cramer recommendations

    Parameters
    ----------
    symbol: str
        Stock ticker
    raw: bool
        Display raw data
    export: str
        Format to export data
    external_axes: Optional[List[plt.Axes]] = None,
        External axes to plot on
