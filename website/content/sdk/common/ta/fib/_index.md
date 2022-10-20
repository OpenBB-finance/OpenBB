To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### common.ta.fib(data: pandas.core.frame.DataFrame, limit: int = 120, start_date: Any = None, end_date: Any = None) -> Tuple[pandas.core.frame.DataFrame, pandas._libs.tslibs.timestamps.Timestamp, pandas._libs.tslibs.timestamps.Timestamp, float, float]

Calculate Fibonacci levels

    Parameters
    ----------
    data : pd.DataFrame
        Dataframe of prices
    limit : int
        Days to look back for retracement
    start_date : Any
        Custom start date for retracement
    end_date : Any
        Custom end date for retracement

    Returns
    -------
    df : pd.DataFrame
        Dataframe of fib levels
    min_date: pd.Timestamp
        Date of min point
    max_date: pd.Timestamp:
        Date of max point
    min_pr: float
        Price at min point
    max_pr: float
        Price at max point

## Getting charts 
### common.ta.fib(data: pandas.core.frame.DataFrame, limit: int = 120, start_date: Optional[str] = None, end_date: Optional[str] = None, symbol: str = '', export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True)

Calculate fibonacci retracement levels

    Parameters
    ----------
    data: pd.DataFrame
        OHLC data
    limit: int
        Days to lookback
    start_date: Optional[str, None]
        User picked date for starting retracement
    end_date: Optional[str, None]
        User picked date for ending retracement
    symbol: str
        Ticker symbol
    export: str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (2 axes are expected in the list), by default None
