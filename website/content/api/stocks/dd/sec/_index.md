To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### stocks.dd.sec(symbol: str) -> pandas.core.frame.DataFrame

Get SEC filings for a given stock ticker. [Source: Market Watch]

    Parameters
    ----------
    symbol : str
        Stock ticker symbol

    Returns
    -------
    df_financials : pd.DataFrame
        SEC filings data

## Getting charts 
### stocks.dd.sec(symbol: str, limit: int = 5, export: str = '', chart=True)

Display SEC filings for a given stock ticker. [Source: Market Watch]

    Parameters
    ----------
    symbol: str
        Stock ticker symbol
    limit: int
        Number of ratings to display
    export: str
        Export dataframe data to csv,json,xlsx file
