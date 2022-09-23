## Get underlying data 
### common.qa.decompose(data: pandas.core.frame.DataFrame, multiplicative: bool = False) -> Tuple[Any, pandas.core.frame.DataFrame, pandas.core.frame.DataFrame]

Perform seasonal decomposition

    Parameters
    ----------
    data : pd.DataFrame
        Dataframe of targeted data
    multiplicative : bool
        Boolean to indicate multiplication instead of addition

    Returns
    -------
    result: Any
        Result of statsmodels seasonal_decompose
    cycle: pd.DataFrame
        Filtered cycle
    trend: pd.DataFrame
        Filtered Trend
