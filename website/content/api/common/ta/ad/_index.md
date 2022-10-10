To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### common.ta.ad(data: pandas.core.frame.DataFrame, use_open: bool = False) -> pandas.core.frame.DataFrame

Calculate AD technical indicator

    Parameters
    ----------
    data : pd.DataFrame
        Dataframe of prices with OHLC and Volume
    use_open : bool
        Whether to use open prices

    Returns
    -------
    pd.DataFrame
        Dataframe with technical indicator

## Getting charts 
### common.ta.ad(data: pandas.core.frame.DataFrame, use_open: bool = False, symbol: str = '', export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True)

Plot AD technical indicator

    Parameters
    ----------
    data : pd.DataFrame
        Dataframe of ohlc prices
    use_open : bool
        Whether to use open prices in calculation
    symbol : str
        Ticker symbol
    export: str
        Format to export data as
    external_axes : Optional[List[plt.Axes]], optional
        External axes (3 axes are expected in the list), by default None
