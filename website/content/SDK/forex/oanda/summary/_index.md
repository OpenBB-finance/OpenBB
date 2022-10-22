To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### forex.oanda.summary(accountID: str = 'REPLACE_ME') -> Union[pandas.core.frame.DataFrame, bool]

Request Oanda account summary.

    Parameters
    ----------
    accountID : str, optional
        Oanda account ID, by default cfg.OANDA_ACCOUNT

    Returns
    -------
    Union[pd.DataFrame, bool]
        Account summary data or False

## Getting charts 
### forex.oanda.summary(accountID: str, chart=True)

Print Oanda account summary.

    Parameters
    ----------
    accountID : str
        Oanda user account ID
