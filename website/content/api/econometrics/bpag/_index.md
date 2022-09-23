To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### econometrics.bpag(model: pandas.core.frame.DataFrame) -> tuple

Calculate test statistics for heteroscedasticity

    Parameters
    ----------
    model : OLS Model
        Model containing residual values.

    Returns
    -------
    Test results from the Breusch-Pagan Test

## Getting charts 
### econometrics.bpag(model: pandas.core.frame.DataFrame, export: str = '', chart=True)

Show Breusch-Pagan heteroscedasticity test

    Parameters
    ----------
    model : OLS Model
        Model containing residual values.
    export : str
        Format to export data
