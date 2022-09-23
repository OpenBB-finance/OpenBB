To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### common.ta.ma(data: pandas.core.series.Series, window: List[int] = None, offset: int = 0, ma_type: str = 'EMA', symbol: str = '', export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None) -> None

Plots MA technical indicator

    Parameters
    ----------
    data: pd.Series
        Series of prices
    window: List[int]
        Length of EMA window
    offset: int
        Offset variable
    ma_type: str
        Type of moving average.  Either "EMA" "ZLMA" or "SMA"
    symbol: str
        Ticker
    export: str
        Format to export data
    external_axes: Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None

## Getting charts 
### common.ta.ma(data: pandas.core.series.Series, window: List[int] = None, offset: int = 0, ma_type: str = 'EMA', symbol: str = '', export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True) -> None

Plots MA technical indicator

    Parameters
    ----------
    data: pd.Series
        Series of prices
    window: List[int]
        Length of EMA window
    offset: int
        Offset variable
    ma_type: str
        Type of moving average.  Either "EMA" "ZLMA" or "SMA"
    symbol: str
        Ticker
    export: str
        Format to export data
    external_axes: Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
