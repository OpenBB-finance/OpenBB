To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### stocks.ba.snews(symbol: str) -> pandas.core.frame.DataFrame

Get headlines sentiment using VADER model over time. [Source: Finnhub]

    Parameters
    ----------
    symbol : str
        Ticker of company

## Getting charts 
### stocks.ba.snews(symbol: str, export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True)

Display stock price and headlines sentiment using VADER model over time. [Source: Finnhub]

    Parameters
    ----------
    symbol : str
        Ticker of company
    export: str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (2 axes are expected in the list), by default None
