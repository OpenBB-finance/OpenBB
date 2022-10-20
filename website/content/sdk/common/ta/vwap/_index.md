To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### common.ta.vwap(data: pandas.core.frame.DataFrame, offset: int = 0) -> pandas.core.frame.DataFrame

Gets volume weighted average price (VWAP)

    Parameters
    ----------
    data: pd.DataFrame
        Dataframe of dates and prices
    offset: int
        Length of offset
    Returns
    ----------
    df_vwap: pd.DataFrame
        Dataframe with VWAP data

## Getting charts 
### common.ta.vwap(data: pandas.core.frame.DataFrame, symbol: str = '', start_date: str = None, end_date: str = None, offset: int = 0, interval: str = '', export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True)

Plots VWMA technical indicator

    Parameters
    ----------
    data : pd.DataFrame
        Dataframe of OHLC prices
    symbol : str
        Ticker
    offset : int
        Offset variable
    start_date: datetime
        Start date to get data from with
    end_date: datetime
        End date to get data from with
    interval : str
        Interval of data
    export : str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (3 axes are expected in the list), by default None
