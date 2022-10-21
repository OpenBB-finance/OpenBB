To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### forex.oanda.opentrades(accountID: str = 'REPLACE_ME') -> Union[pandas.core.frame.DataFrame, bool]

Request open trades data.

    Parameters
    ----------
    accountID : str, optional
        Oanda account ID, by default cfg.OANDA_ACCOUNT

    Returns
    -------
    Union[pd.DataFrame, bool]
        Open trades data or False

## Getting charts 
### forex.oanda.opentrades(accountID: str, chart=True)

View open trades.

    Parameters
    ----------
    accountID : str
        Oanda user account ID
