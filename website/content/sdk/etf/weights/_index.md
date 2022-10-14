To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### etf.weights(name: str) -> Dict

Return sector weightings allocation of ETF. [Source: Yahoo Finance]

    Parameters
    ----------
    name: str
        ETF name

    Returns
    ----------
    Dict
        Dictionary with sector weightings allocation

## Getting charts 
### etf.weights(name: str, raw: bool = False, min_pct_to_display: float = 5, export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True)

Display sector weightings allocation of ETF. [Source: Yahoo Finance]

    Parameters
    ----------
    name: str
        ETF name
    raw: bool
        Display sector weighting allocation
    min_pct_to_display: float
        Minimum percentage to display sector
    export: str
        Type of format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
