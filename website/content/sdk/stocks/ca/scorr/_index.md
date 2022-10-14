To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### stocks.ca.scorr(similar: List[str])

Get correlation sentiments across similar companies. [Source: FinBrain]

    Parameters
    ----------
    similar : List[str]
        Similar companies to compare income with.
        Comparable companies can be accessed through
        finnhub_peers(), finviz_peers(), polygon_peers().

## Getting charts 
### stocks.ca.scorr(similar: List[str], raw: bool = False, export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True)

Plot correlation sentiments heatmap across similar companies. [Source: FinBrain]

    Parameters
    ----------
    similar : List[str]
        Similar companies to compare income with.
        Comparable companies can be accessed through
        finviz_peers(), finnhub_peers() or polygon_peers().
    raw : bool, optional
        Output raw values, by default False
    export : str, optional
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
