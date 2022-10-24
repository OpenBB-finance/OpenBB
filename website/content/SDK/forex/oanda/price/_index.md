To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### forex.oanda.price(accountID: str = 'REPLACE_ME', instrument: Optional[str] = None) -> Union[Dict[str, str], bool]

Request price for a forex pair.

    Parameters
    ----------
    accountID : str, optional
        Oanda account ID, by default cfg.OANDA_ACCOUNT
    instrument : Union[str, None]
        The loaded currency pair, by default None

    Returns
    -------
    Union[Dict[str, str], bool]
        The currency pair price or False

## Getting charts 
### forex.oanda.price(account: str, instrument: Optional[str] = '', chart=True)

View price for loaded currency pair.

    Parameters
    ----------
    accountID : str
        Oanda account ID
    instrument : Union[str, None]
        Instrument code or None
