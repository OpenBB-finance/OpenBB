To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### stocks.fa.yf_financials(symbol: str, statement: str, ratios: bool = False) -> pandas.core.frame.DataFrame

Get cashflow statement for company

    Parameters
    ----------
    symbol : str
        Stock ticker symbol
    statement: str
        can be:
            cash-flow
            financials for Income
            balance-sheet
    ratios: bool
        Shows percentage change

    Returns
    -------
    pd.DataFrame
        Dataframe of Financial statement

## Getting charts 
### stocks.fa.yf_financials(symbol: str, statement: str, limit: int = 12, ratios: bool = False, plot: list = None, export: str = '', chart=True)

Display tickers balance sheet, income statement or cash-flow

    Parameters
    ----------
    symbol: str
        Stock ticker symbol
    statement: str
        can be:
            cash-flow
            financials for Income
            balance-sheet
    limit: int
    ratios: bool
        Shows percentage change
    plot: list
        List of row labels to plot
    export: str
        Format to export data
