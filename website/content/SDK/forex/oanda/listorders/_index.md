To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### forex.oanda.listorders(order_state: str = 'PENDING', order_count: int = 0, accountID: str = 'REPLACE_ME') -> Union[pandas.core.frame.DataFrame, bool]

Request the orders list from Oanda.

    Parameters
    ----------
    order_state : str
        Filter orders by a specific state ("PENDING", "CANCELLED", etc.)
    order_count : int
        Limit the number of orders to retrieve
    accountID : str, optional
        Oanda account ID, by default cfg.OANDA_ACCOUNT

## Getting charts 
### forex.oanda.listorders(accountID: str, order_state: str = 'PENDING', order_count: int = 0, chart=True)

List order history.

    Parameters
    ----------
    accountID : str
        Oanda user account ID
    order_state : str
        Filter orders by a specific state ("PENDING", "CANCELLED", etc.)
    order_count : int
        Limit the number of orders to retrieve
