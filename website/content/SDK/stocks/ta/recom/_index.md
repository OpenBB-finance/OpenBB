To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### stocks.ta.recom(symbol: str, screener: str = 'america', exchange: str = '', interval: str = '') -> pandas.core.frame.DataFrame

Get tradingview recommendation based on technical indicators

    Parameters
    ----------
    symbol : str
        Ticker symbol to get the recommendation from tradingview based on technical indicators
    screener : str
        Screener based on tradingview docs https://python-tradingview-ta.readthedocs.io/en/latest/usage.html
    exchange: str
        Exchange based on tradingview docs https://python-tradingview-ta.readthedocs.io/en/latest/usage.html
    interval: str
        Interval time to check technical indicators and correspondent recommendation

    Returns
    -------
    df_recommendation: pd.DataFrame
        Dataframe of tradingview recommendations based on technical indicators

## Getting charts 
### stocks.ta.recom(symbol: str, screener: str = 'america', exchange: str = '', interval: str = '', export: str = '', chart=True)

Print tradingview recommendation based on technical indicators

    Parameters
    ----------
    symbol : str
        Ticker symbol to get tradingview recommendation based on technical indicators
    screener : str
        Screener based on tradingview docs https://python-tradingview-ta.readthedocs.io/en/latest/usage.html
    exchange: str
        Exchange based on tradingview docs https://python-tradingview-ta.readthedocs.io/en/latest/usage.html
    interval: str
        Interval time to check technical indicators and correspondent recommendation
    export: str
        Format of export file
