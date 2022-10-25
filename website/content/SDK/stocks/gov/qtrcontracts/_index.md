To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### stocks.gov.qtrcontracts(analysis: str = 'total', limit: int = 5) -> pandas.core.frame.DataFrame

Analyzes quarterly contracts by ticker

    Parameters
    ----------
    analysis : str
        How to analyze.  Either gives total amount or sorts by high/low momentum.
    limit : int, optional
        Number to return, by default 5

    Returns
    -------
    pd.DataFrame
        Dataframe with tickers and total amount if total selected.

## Getting charts 
### stocks.gov.qtrcontracts(analysis: str = 'total', limit: int = 5, raw: bool = False, export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True)

Quarterly contracts [Source: quiverquant.com]

    Parameters
    ----------
    analysis: str
        Analysis to perform.  Either 'total', 'upmom' 'downmom'
    limit: int
        Number to show
    raw: bool
        Flag to display raw data
    export: str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
