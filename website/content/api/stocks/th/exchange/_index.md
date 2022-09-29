To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### stocks.th.exchange(symbol: str) -> pandas.core.frame.DataFrame

Get current exchange open hours.

    Parameters
    ----------
    symbol : str
        Exchange symbol

    Returns
    -------
    pd.DataFrame
        Exchange info

## Getting charts 
### stocks.th.exchange(symbol: str, chart=True)

Display current exchange trading hours.

    Parameters
    ----------
    symbol : str
        Exchange symbol
