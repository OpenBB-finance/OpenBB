To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### forex.oanda.positionbook(instrument: Optional[str] = None, accountID: str = 'REPLACE_ME') -> Union[pandas.core.frame.DataFrame, bool]

Request position book data for plotting.

    Parameters
    ----------
    instrument : Union[str, None]
        The loaded currency pair, by default None
    accountID : str, optional
        Oanda account ID, by default cfg.OANDA_ACCOUNT

    Returns
    -------
    Union[pd.DataFrame, bool]
        Position book data or False

## Getting charts 
### forex.oanda.positionbook(accountID: str, instrument: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True)

Plot a position book for an instrument if Oanda provides one.

    Parameters
    ----------
    accountID : str
        Oanda user account ID
    instrument : str
        The loaded currency pair
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
