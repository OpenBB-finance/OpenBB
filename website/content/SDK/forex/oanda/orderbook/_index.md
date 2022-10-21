To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### forex.oanda.orderbook(instrument: Optional[str] = None, accountID: str = 'REPLACE_ME') -> Union[pandas.core.frame.DataFrame, bool]

Request order book data for plotting.

    Parameters
    ----------
    instrument : Union[str, None]
        The loaded currency pair, by default None
    accountID : str, optional
        Oanda account ID, by default cfg.OANDA_ACCOUNT

    Returns
    -------
    Union[pd.DataFrame, bool]
        Order book data or False

## Getting charts 
### forex.oanda.orderbook(accountID: str, instrument: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True)


    Plot the orderbook for the instrument if Oanda provides one.

    Parameters
    ----------
    accountID : str
        Oanda user account ID
    instrument : str
        The loaded currency pair
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
