To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### forex.oanda.pending(accountID: str = 'REPLACE_ME') -> Union[pandas.core.frame.DataFrame, bool]

Request information on pending orders.

    Parameters
    ----------
    accountID : str, optional
        Oanda account ID, by default cfg.OANDA_ACCOUNT

    Returns
    -------
    Union[pd.DataFrame, bool]
        Pending orders data or False

## Getting charts 
### forex.oanda.pending(accountID: str, chart=True)

Get information about pending orders.

    Parameters
    ----------
    accountID : str
        Oanda user account ID
