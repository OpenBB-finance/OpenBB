To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### stocks.gov.contracts(symbol: str, past_transaction_days: int = 10) -> pandas.core.frame.DataFrame

Get government contracts for ticker [Source: quiverquant.com]

    Parameters
    ----------
    symbol: str
        Ticker to get congress trading data from
    past_transaction_days: int
        Number of days to get transactions for

    Returns
    -------
    pd.DataFrame
        Most recent transactions by members of U.S. Congress

## Getting charts 
### stocks.gov.contracts(symbol: str, past_transaction_days: int = 10, raw: bool = False, export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True)

Show government contracts for ticker [Source: quiverquant.com]

    Parameters
    ----------
    symbol: str
        Ticker to get congress trading data from
    past_transaction_days: int
        Number of days to get transactions for
    raw: bool
        Flag to display raw data
    export: str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
