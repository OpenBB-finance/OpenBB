To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### common.qa.es(data: pandas.core.frame.DataFrame, use_mean: bool = False, distribution: str = 'normal', percentile: Union[float, int] = 99.9, portfolio: bool = False) -> pandas.core.frame.DataFrame

Gets Expected Shortfall for specified stock dataframe

    Parameters
    ----------
    data: pd.DataFrame
        Data dataframe
    use_mean: bool
        If one should use the data mean for calculation
    distribution: str
        Type of distribution, options: laplace, student_t, normal
    percentile: Union[float,int]
        VaR percentile
    portfolio: bool
        If the data is a portfolio

    Returns
    -------
    list
        list of ES
    list
        list of historical ES

## Getting charts 
### common.qa.es(data: pandas.core.frame.DataFrame, symbol: str = '', use_mean: bool = False, distribution: str = 'normal', percentile: float = 99.9, portfolio: bool = False, chart=True) -> None

Displays expected shortfall

    Parameters
    ----------
    data: pd.DataFrame
        Data dataframe
    use_mean:
        if one should use the data mean return
    symbol: str
        name of the data
    distribution: str
        choose distribution to use: logistic, laplace, normal
    percentile: int
        es percentile
    portfolio: bool
        If the data is a portfolio
