To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### stocks.fa.av_cash(symbol: str, limit: int = 5, quarterly: bool = False, ratios: bool = False, plot: bool = False) -> pandas.core.frame.DataFrame

Get cash flows for company

    Parameters
    ----------
    symbol : str
        Stock ticker symbol
    limit : int
        Number of past to get
    quarterly : bool, optional
        Flag to get quarterly instead of annual, by default False
    ratios: bool
        Shows percentage change, by default False
    plot: bool
        If the data shall be formatted ready to plot

    Returns
    -------
    pd.DataFrame
        Dataframe of cash flow statements

## Getting charts 
### stocks.fa.av_cash(symbol: str, limit: int = 5, quarterly: bool = False, ratios: bool = False, plot: list = None, export: str = '', chart=True)

Alpha Vantage income statement

    Parameters
    ----------
    symbol : str
        Fundamental analysis ticker symbol
    limit: int
        Number of past statements, by default 5
    quarterly: bool
        Flag to get quarterly instead of annual, by default False
    ratios: bool
        Shows percentage change, by default False
    plot: list
        List of row labels to plot
    export: str
        Format to export data
