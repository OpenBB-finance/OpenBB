To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### stocks.gov.gtrades(symbol: str, gov_type: str = 'congress', past_transactions_months: int = 6) -> pandas.core.frame.DataFrame

Government trading for specific ticker [Source: quiverquant.com]

    Parameters
    ----------
    symbol: str
        Ticker symbol to get congress trading data from
    gov_type: str
        Type of government data between: congress, senate and house
    past_transactions_months: int
        Number of months to get transactions for

    Returns
    -------
    pd.DataFrame
        DataFrame of tickers government trading

## Getting charts 
### stocks.gov.gtrades(symbol: str, gov_type: str = 'congress', past_transactions_months: int = 6, raw: bool = False, export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True)

Government trading for specific ticker [Source: quiverquant.com]

    Parameters
    ----------
    symbol: str
        Ticker symbol to get congress trading data from
    gov_type: str
        Type of government data between: congress, senate and house
    past_transactions_months: int
        Number of months to get transactions for
    raw: bool
        Show raw output of trades
    export: str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
