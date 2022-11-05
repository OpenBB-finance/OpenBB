To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### common.ta.macd(data: pandas.core.series.Series, n_fast: int = 12, n_slow: int = 26, n_signal: int = 9) -> pandas.core.frame.DataFrame

Moving average convergence divergence

    Parameters
    ----------
    data: pd.Series
        Values for calculation
    n_fast : int
        Fast period
    n_slow : int
        Slow period
    n_signal : int
        Signal period
    Returns
    ----------
    pd.DataFrame
        Dataframe of technical indicator

## Getting charts 
### common.ta.macd(data: pandas.core.series.Series, n_fast: int = 12, n_slow: int = 26, n_signal: int = 9, symbol: str = '', export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True)

Plot MACD signal

    Parameters
    ----------
    data : pd.Series
        Values to input
    n_fast : int
        Fast period
    n_slow : int
        Slow period
    n_signal : int
        Signal period
    symbol : str
        Stock ticker
    export : str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (2 axes are expected in the list), by default None
