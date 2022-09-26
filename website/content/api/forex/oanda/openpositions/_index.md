To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### forex.oanda.openpositions(accountID: str = 'REPLACE_ME') -> Union[pandas.core.frame.DataFrame, bool]

Request information on open positions.

    Parameters
    ----------
    accountID : str, optional
        Oanda account ID, by default cfg.OANDA_ACCOUNT

## Getting charts 
### forex.oanda.openpositions(accountID: str, chart=True)

Get information about open positions.

    Parameters
    ----------
    accountID : str
        Oanda user account ID
