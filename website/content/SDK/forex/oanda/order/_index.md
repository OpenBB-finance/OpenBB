To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### forex.oanda.order(price: int = 0, units: int = 0, instrument: Optional[str] = None, accountID: str = 'REPLACE_ME') -> Union[pandas.core.frame.DataFrame, bool]

Request creation of buy/sell trade order.

    Parameters
    ----------
    instrument : Union[str, None]
        The loaded currency pair, by default None
    price : int
        The price to set for the limit order.
    units : int
        The number of units to place in the order request.
    accountID : str, optional
        Oanda account ID, by default cfg.OANDA_ACCOUNT

    Returns
    -------
    Union[pd.DataFrame, bool]
        Orders data or False

## Getting charts 
### forex.oanda.order(accountID: str, instrument: str = '', price: int = 0, units: int = 0, chart=True)

Create a buy/sell order.

    Parameters
    ----------
    accountID : str
        Oanda user account ID
    instrument : str
        The loaded currency pair
    price : int
        The price to set for the limit order.
    units : int
        The number of units to place in the order request.
