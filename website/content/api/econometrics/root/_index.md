To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### econometrics.root(data: pandas.core.series.Series, fuller_reg: str = 'c', kpss_reg: str = 'c') -> pandas.core.frame.DataFrame

Calculate test statistics for unit roots

    Parameters
    ----------
    data : pd.Series
        Series or column of DataFrame of target variable
    fuller_reg : str
        Type of regression of ADF test
    kpss_reg : str
        Type of regression for KPSS test

    Returns
    -------
    pd.DataFrame
        Dataframe with results of ADF test and KPSS test

## Getting charts 
### econometrics.root(data: pandas.core.series.Series, dataset: str = '', column: str = '', fuller_reg: str = 'c', kpss_reg: str = 'c', export: str = '', chart=True)

Determine the normality of a timeseries.

    Parameters
    ----------
    data : pd.Series
        Series of target variable
    dataset: str
        Name of the dataset
    column: str
        Name of the column
    fuller_reg : str
        Type of regression of ADF test. Choose c, ct, ctt, or nc
    kpss_reg : str
        Type of regression for KPSS test. Choose c or ct
    export: str
        Format to export data.
