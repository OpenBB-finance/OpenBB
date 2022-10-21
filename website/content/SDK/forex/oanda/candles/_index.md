To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### forex.oanda.candles(instrument: Optional[str] = None, granularity: str = 'D', candlecount: int = 180) -> Union[pandas.core.frame.DataFrame, bool]

Request data for candle chart.

    Parameters
    ----------
    instrument : str
        Loaded currency pair code
    granularity : str, optional
        Data granularity, by default "D"
    candlecount : int, optional
        Limit for the number of data points, by default 180

    Returns
    -------
    Union[pd.DataFrame, bool]
        Candle chart data or False

## Getting charts 
### forex.oanda.candles(instrument: str = '', granularity: str = 'D', candlecount: int = 180, additional_charts: Optional[Dict[str, bool]] = None, external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True)

Show candle chart.

    Note that additional plots (ta indicators) not supported in external axis mode.

    Parameters
    ----------
    instrument : str
        The loaded currency pair
    granularity : str, optional
        The timeframe to get for the candle chart. Seconds: S5, S10, S15, S30
        Minutes: M1, M2, M4, M5, M10, M15, M30 Hours: H1, H2, H3, H4, H6, H8, H12
        Day (default): D, Week: W Month: M,
    candlecount : int, optional
        Limit for the number of data points
    additional_charts : Dict[str, bool]
        A dictionary of flags to include additional charts
    external_axes : Optional[List[plt.Axes]], optional
        External axes (2 axes are expected in the list), by default None
