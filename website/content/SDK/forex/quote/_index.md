To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### forex.quote(to_symbol: str = 'USD', from_symbol: str = 'EUR') -> Dict

Get current exchange rate quote from alpha vantage.

    Parameters
    ----------
    to_symbol : str
        To forex symbol
    from_symbol : str
        From forex symbol

    Returns
    -------
    Dict
        Dictionary of exchange rate

## Getting charts 
### forex.quote(to_symbol: str = 'USD', from_symbol: str = 'EUR', chart=True)

Display current forex pair exchange rate.

    Parameters
    ----------
    to_symbol : str
        To symbol
    from_symbol : str
        From forex symbol
