To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### common.qa.sharpe(data: pandas.core.frame.DataFrame, rfr: float = 0, window: float = 252) -> pandas.core.frame.DataFrame

Calculates the sharpe ratio
    Parameters
    ----------
    data: pd.DataFrame
        selected dataframe column
    rfr: float
        risk free rate
    window: float
        length of the rolling window

    Returns
    -------
    sharpe: pd.DataFrame
        sharpe ratio

## Getting charts 
### common.qa.sharpe(data: pandas.core.frame.DataFrame, rfr: float = 0, window: float = 252, chart=True) -> None

Calculates the sharpe ratio
    Parameters
    ----------
    data: pd.DataFrame
        selected dataframe column
    rfr: float
        risk free rate
    window: float
        length of the rolling window
