To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### econometrics.bgod(model: pandas.core.frame.DataFrame, lags: int = 3) -> tuple

Calculate test statistics for autocorrelation

    Parameters
    ----------
    model : OLS Model
        Model containing residual values.
    lags : int
        The amount of lags.

    Returns
    -------
    Test results from the Breusch-Godfrey Test

## Getting charts 
### econometrics.bgod(model: pandas.core.frame.DataFrame, lags: int = 3, export: str = '', chart=True)

Show Breusch-Godfrey autocorrelation test

    Parameters
    ----------
    model : OLS Model
        Model containing residual values.
    lags : int
        The amount of lags included.
    export : str
        Format to export data
