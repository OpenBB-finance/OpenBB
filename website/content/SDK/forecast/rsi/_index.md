## Get underlying data 
### forecast.rsi(dataset: pandas.core.frame.DataFrame, target_column: str = 'close', period: int = 10) -> pandas.core.frame.DataFrame

A momentum indicator that measures the magnitude of recent price changes to evaluate
    overbought or oversold conditions in the price of a stock or other asset.

    Parameters
    ----------
    dataset : pd.DataFrame
        The dataset you wish to calculate for
    target_column : str
        The column you wish to add the RSI to
    period : int
        Time Span

    Returns
    -------
    pd.DataFrame:
        Dataframe with added RSI column
