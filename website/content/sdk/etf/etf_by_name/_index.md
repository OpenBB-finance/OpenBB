To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### etf.etf_by_name(name_to_search: str) -> pandas.core.frame.DataFrame

Get an ETF symbol and name based on ETF string to search. [Source: StockAnalysis]

    Parameters
    ----------
    name_to_search: str
        ETF name to match

    Returns
    -------
    df: pd.Dataframe
        Dataframe with symbols and names

## Getting charts 
### etf.etf_by_name(name: str, limit: int = 10, export: str = '', chart=True)

Display ETFs matching search string. [Source: StockAnalysis]

    Parameters
    ----------
    name: str
        String being matched
    limit: int
        Limit of ETFs to display
    export: str
        Export to given file type

