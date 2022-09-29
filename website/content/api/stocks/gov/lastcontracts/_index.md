To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### stocks.gov.lastcontracts(past_transaction_days: int = 2) -> pandas.core.frame.DataFrame

Get last government contracts [Source: quiverquant.com]

    Parameters
    ----------
    past_transaction_days: int
        Number of days to look back

    Returns
    -------
    pd.DataFrame
        DataFrame of government contracts

## Getting charts 
### stocks.gov.lastcontracts(past_transaction_days: int = 2, limit: int = 20, sum_contracts: bool = False, export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True)

Last government contracts [Source: quiverquant.com]

    Parameters
    ----------
    past_transaction_days: int
        Number of days to look back
    limit: int
        Number of contracts to show
    sum_contracts: bool
        Flag to show total amount of contracts given out.
    export: str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
