To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### stocks.ta.rsp(s_ticker: str = '') -> Tuple[pandas.core.frame.DataFrame]

Relative strength percentile [Source: https://github.com/skyte/relative-strength]
    Currently takes from https://github.com/soggyomelette/rs-log in order to get desired output

    Parameters
    ----------
    s_ticker : str
        Stock Ticker

    Returns
    ----------
    pd.DataFrame
        Dataframe of stock percentile
    pd.Dataframe
        Dataframe of industry percentile
    pd.Dataframe
        Raw stock dataframe for export
    pd.Dataframe
        Raw industry dataframe for export

## Getting charts 
### stocks.ta.rsp(s_ticker: str = '', export: str = '', tickers_show: bool = False, chart=True)

Display Relative Strength Percentile [Source: https://github.com/skyte/relative-strength]

    Parameters
    ----------
    s_ticker : str
        Stock ticker
    export : str
        Format of export file
    tickers_show : bool
        Boolean to check if tickers in the same industry as the stock should be shown
