To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### forex.oanda.close(orderID: str, units: Optional[int] = 0, accountID: str = 'REPLACE_ME') -> Union[pandas.core.frame.DataFrame, bool]

Close a trade.

    Parameters
    ----------
    orderID : str
        ID of the order to close
    units : Union[int, None]
        Number of units to close. If empty default to all.
    accountID : str, optional
        Oanda account ID, by default cfg.OANDA_ACCOUNT

    Returns
    -------
    Union[pd.DataFrame, bool]
        Close trades data or False

## Getting charts 
### forex.oanda.close(accountID: str, orderID: str = '', units: Optional[int] = None, chart=True)

Close a trade.

    Parameters
    ----------
    accountID : str
        Oanda user account ID
    orderID : str
        ID of the order to close
    units : Union[int, None]
        Number of units to close. If empty default to all.
