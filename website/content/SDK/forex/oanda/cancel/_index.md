To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### forex.oanda.cancel(orderID: str, accountID: str = 'REPLACE_ME') -> Union[str, bool]

Request cancellation of a pending order.

    Parameters
    ----------
    orderID : str
        The pending order ID to cancel.
    accountID : str, optional
        Oanda account ID, by default cfg.OANDA_ACCOUNT

## Getting charts 
### forex.oanda.cancel(accountID: str, orderID: str = '', chart=True)

Cancel a Pending Order.

    Parameters
    ----------
    accountID : str
        Oanda user account ID
    orderID : str
        The pending order ID to cancel.
