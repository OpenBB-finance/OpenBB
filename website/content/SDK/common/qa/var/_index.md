To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### common.qa.var(data: pandas.core.frame.DataFrame, use_mean: bool = False, adjusted_var: bool = False, student_t: bool = False, percentile: Union[int, float] = 99.9, portfolio: bool = False) -> pandas.core.frame.DataFrame

Gets value at risk for specified stock dataframe

    Parameters
    ----------
    data: pd.DataFrame
        Data dataframe
    use_mean: bool
        If one should use the data mean for calculation
    adjusted_var: bool
        If one should return VaR adjusted for skew and kurtosis
    student_t: bool
        If one should use the student-t distribution
    percentile: Union[int,float]
        VaR percentile
    portfolio: bool
        If the data is a portfolio

    Returns
    -------
    list
        list of VaR
    list
        list of historical VaR

## Getting charts 
### common.qa.var(data: pandas.core.frame.DataFrame, symbol: str = '', use_mean: bool = False, adjusted_var: bool = False, student_t: bool = False, percentile: float = 99.9, data_range: int = 0, portfolio: bool = False, chart=True) -> None

Displays VaR of dataframe

    Parameters
    ----------
    data: pd.Dataframe
        Data dataframe
    use_mean: bool
        if one should use the data mean return
    symbol: str
        name of the data
    adjusted_var: bool
        if one should have VaR adjusted for skew and kurtosis (Cornish-Fisher-Expansion)
    student_t: bool
        If one should use the student-t distribution
    percentile: int
        var percentile
    data_range: int
        Number of rows you want to use VaR over
    portfolio: bool
        If the data is a portfolio
