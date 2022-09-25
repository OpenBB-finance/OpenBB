To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### forex.oanda.fwd(to_symbol: str = 'USD', from_symbol: str = 'EUR')

Gets forward rates from fxempire

    Parameters
    ----------
    to_symbol: str
        To currency
    from_symbol: str
        From currency

    Returns
    -------
    df: pd.DataFrame


## Getting charts 
### forex.oanda.fwd(to_symbol: str = 'USD', from_symbol: str = 'EUR', export: str = '', chart=True)

Display forward rates for currency pairs

    Parameters
    ----------
    to_symbol: str
        To currency
    from_symbol: str
        From currency
    export: str
        Format to export data
