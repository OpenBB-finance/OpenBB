To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### common.qa.unitroot(data: pandas.core.frame.DataFrame, fuller_reg: str = 'c', kpss_reg: str = 'c') -> pandas.core.frame.DataFrame

Calculate test statistics for unit roots

    Parameters
    ----------
    data : pd.DataFrame
        DataFrame of target variable
    fuller_reg : str
        Type of regression of ADF test. Can be ‘c’,’ct’,’ctt’,’nc’ 'c' - Constant and t - trend order
    kpss_reg : str
        Type of regression for KPSS test.  Can be ‘c’,’ct'

    Returns
    -------
    pd.DataFrame
        Dataframe with results of ADF test and KPSS test

## Getting charts 
### common.qa.unitroot(data: pandas.core.frame.DataFrame, target: str, fuller_reg: str = 'c', kpss_reg: str = 'c', export: str = '', chart=True)

Show unit root test calculations

    Parameters
    ----------
    data : pd.DataFrame
        DataFrame
    target : str
        Column of data to look at
    fuller_reg : str
        Type of regression of ADF test. Can be ‘c’,’ct’,’ctt’,’nc’ 'c' - Constant and t - trend order
    kpss_reg : str
        Type of regression for KPSS test. Can be ‘c’,’ct'
    export : str
        Format for exporting data
