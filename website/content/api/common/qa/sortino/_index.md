To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### common.qa.sortino(data: pandas.core.frame.DataFrame, target_return: float = 0, window: float = 252, adjusted: bool = False) -> pandas.core.frame.DataFrame

Calculates the sortino ratio
    Parameters
    ----------
    data: pd.DataFrame
        selected dataframe
    target_return: float
        target return of the asset
    window: float
        length of the rolling window
    adjusted: bool
        adjust the sortino ratio

    Returns
    -------
    sortino: pd.DataFrame
        sortino ratio

## Getting charts 
### common.qa.sortino(data: pandas.core.frame.DataFrame, target_return: float, window: float, adjusted: bool, chart=True) -> None

Displays the sortino ratio
    Parameters
    ----------
    data: pd.DataFrame
        selected dataframe
    target_return: float
        target return of the asset
    window: float
        length of the rolling window
    adjusted: bool
        adjust the sortino ratio
