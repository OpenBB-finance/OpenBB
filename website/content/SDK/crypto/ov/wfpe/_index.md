To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### crypto.ov.wfpe(symbol: str) -> List[Any]

Scrapes coin withdrawal fees per exchange
    [Source: https://withdrawalfees.com/]

    Parameters
    ----------
    symbol: str
        Coin to check withdrawal fees. By default bitcoin
    Returns
    -------
    List:
        - str:              Overall statistics (exchanges, lowest, average and median)
        - pandas.DataFrame: Exchange, Withdrawal Fee, Minimum Withdrawal Amount

## Getting charts 
### crypto.ov.wfpe(symbol: str, export: str = '', chart=True) -> None

Coin withdrawal fees per exchange
    [Source: https://withdrawalfees.com/]

    Parameters
    ----------
    symbol: str
        Coin to check withdrawal fees
    export : str
        Export dataframe data to csv,json,xlsx file
