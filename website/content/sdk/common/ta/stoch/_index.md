To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### common.ta.stoch(high_vals: pandas.core.series.Series, low_vals: pandas.core.series.Series, close_vals: pandas.core.series.Series, fastkperiod: int = 14, slowdperiod: int = 3, slowkperiod: int = 3)

Stochastic oscillator

    Parameters
    ----------
    high_vals: pd.Series
        High values
    low_vals: pd.Series
        Low values
    close-vals: pd.Series
        Close values
    fastkperiod : int
        Fast k period
    slowdperiod : int
        Slow d period
    slowkperiod : int
        Slow k period
    Returns
    ----------
    pd.DataFrame
        Dataframe of technical indicator

## Getting charts 
### common.ta.stoch(data: pandas.core.frame.DataFrame, fastkperiod: int = 14, slowdperiod: int = 3, slowkperiod: int = 3, symbol: str = '', export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True) -> None

Plot stochastic oscillator signal

    Parameters
    ----------
    data : pd.DataFrame
        Dataframe of OHLC prices
    fastkperiod : int
        Fast k period
    slowdperiod : int
        Slow d period
    slowkperiod : int
        Slow k period
    symbol : str
        Stock ticker symbol
    export : str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (3 axes are expected in the list), by default None
