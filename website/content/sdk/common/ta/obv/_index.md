To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### common.ta.obv(data: pandas.core.frame.DataFrame) -> pandas.core.frame.DataFrame

On Balance Volume

    Parameters
    ----------
    data: pd.DataFrame
        Dataframe of OHLC prices

    Returns
    -------
    pd.DataFrame
        Dataframe with technical indicator

## Getting charts 
### common.ta.obv(data: pandas.core.frame.DataFrame, symbol: str = '', export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True)

Plot OBV technical indicator

    Parameters
    ----------
    data : pd.DataFrame
        Dataframe of ohlc prices
    symbol : str
        Ticker
    export: str
        Format to export data as
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
