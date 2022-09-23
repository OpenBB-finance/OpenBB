To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### common.ta.adosc(data: pandas.core.frame.DataFrame, use_open: bool = False, fast: int = 3, slow: int = 10) -> pandas.core.frame.DataFrame

Calculate AD oscillator technical indicator

    Parameters
    ----------
    data : pd.DataFrame
        Dataframe of OHLC prices
    use_open : bool
        Whether to use open prices
    fast: int
        Fast value
    slow: int
        Slow value

    Returns
    -------
    pd.DataFrame
        Dataframe with technical indicator

## Getting charts 
### common.ta.adosc(data: pandas.core.frame.DataFrame, fast: int = 3, slow: int = 10, use_open: bool = False, symbol: str = '', export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True)

Display AD Osc Indicator

    Parameters
    ----------
    data : pd.DataFrame
        Dataframe of ohlc prices
    use_open : bool
        Whether to use open prices in calculation
    fast: int
         Length of fast window
    slow : int
        Length of slow window
    symbol : str
        Stock ticker
    export : str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (3 axes are expected in the list), by default None
