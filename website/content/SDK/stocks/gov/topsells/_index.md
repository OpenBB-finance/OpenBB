To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### stocks.gov.topsells(gov_type: str = 'congress', past_transactions_months: int = 6) -> pandas.core.frame.DataFrame

Get top sell government trading [Source: quiverquant.com]

    Parameters
    ----------
    gov_type: str
        Type of government data between: congress, senate and house
    past_transactions_months: int
        Number of months to get trading for

    Returns
    -------
    pd.DataFrame
        DataFrame of top government sell trading

## Getting charts 
### stocks.gov.topsells(gov_type: str = 'congress', past_transactions_months: int = 6, limit: int = 10, raw: bool = False, export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True)

Top sell government trading [Source: quiverquant.com]

    Parameters
    ----------
    gov_type: str
        Type of government data between: congress, senate and house
    past_transactions_months: int
        Number of months to get trading for
    limit: int
        Number of tickers to show
    raw: bool
        Display raw data
    export: str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
