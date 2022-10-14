To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### stocks.fa.poly_financials(symbol: str, statement: str, quarterly: bool = False, ratios: bool = False) -> pandas.core.frame.DataFrame

Get ticker financial statements from polygon

    Parameters
    ----------
    symbol: str
        Stock ticker symbol
    statement: str
        Financial statement data to retrieve, can be balance, income or cash
    quarterly:bool
        Flag to get quarterly reports, by default False
    ratios: bool
        Shows percentage change, by default False

    Returns
    -------
    pd.DataFrame
        Balance Sheets or Income Statements

## Getting charts 
### stocks.fa.poly_financials(symbol: str, statement: str, limit: int = 10, quarterly: bool = False, ratios: bool = False, plot: list = None, export: str = '', chart=True)

Display tickers balance sheet or income statement

    Parameters
    ----------
    symbol: str
        Stock ticker symbol
    statement:str
        Either balance or income
    limit: int
        Number of results to show, by default 10
    quarterly: bool
        Flag to get quarterly reports, by default False
    ratios: bool
        Shows percentage change, by default False
    plot: list
        List of row labels to plot
    export: str
        Format to export data
