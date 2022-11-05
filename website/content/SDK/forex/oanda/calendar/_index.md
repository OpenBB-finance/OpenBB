To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### forex.oanda.calendar(days: int = 14, instrument: Optional[str] = None) -> Union[pandas.core.frame.DataFrame, bool]

Request data of significant events calendar.

    Parameters
    ----------
    instrument : Union[str, None]
        The loaded currency pair, by default None
    days : int
        Number of days in advance

    Returns
    -------
    Union[pd.DataFrame, bool]
        Calendar events data or False

## Getting charts 
### forex.oanda.calendar(instrument: str, days: int = 7, chart=True)

View calendar of significant events.

    Parameters
    ----------
    instrument : str
        The loaded currency pair
    days : int
        Number of days in advance
