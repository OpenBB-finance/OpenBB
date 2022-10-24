## Get underlying data 
### forecast.roc(dataset: pandas.core.frame.DataFrame, target_column: str = 'close', period: int = 10) -> pandas.core.frame.DataFrame

A momentum oscillator, which measures the percentage change between the current
    value and the n period past value.

    Parameters
    ----------
    dataset : pd.DataFrame
        The dataset you wish to calculate with
    target_column : str
        The column you wish to add the ROC to
    period : int
        Time Span

    Returns
    -------
    pd.DataFrame:
        Dataframe with added ROC column
