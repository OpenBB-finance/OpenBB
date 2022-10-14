To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### econometrics.dwat(residual: pandas.core.frame.DataFrame) -> pandas.core.frame.DataFrame

Calculate test statistics for Durbing Watson autocorrelation

    Parameters
    ----------
    residual : OLS Model
        Model containing residual values.

    Returns
    -------
    Test statistic of the Durbin Watson test.

## Getting charts 
### econometrics.dwat(dependent_variable: pandas.core.series.Series, residual: pandas.core.frame.DataFrame, plot: bool = False, export: str = '', external_axes: Optional[List[axes]] = None, chart=True)

Show Durbin-Watson autocorrelation tests

    Parameters
    ----------
    dependent_variable : pd.Series
        The dependent variable.
    residual : OLS Model
        The residual of an OLS model.
    plot : bool
        Whether to plot the residuals
    export : str
        Format to export data
    external_axes: Optional[List[plt.axes]]
        External axes to plot on
