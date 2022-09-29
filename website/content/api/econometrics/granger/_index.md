To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### econometrics.granger(dependent_series, independent_series, lags)

Calculate granger tests

    Parameters
    ----------
    dependent_series: Series
        The series you want to test Granger Causality for.
    independent_series: Series
        The series that you want to test whether it Granger-causes time_series_y
    lags : int
        The amount of lags for the Granger test. By default, this is set to 3.

## Getting charts 
### econometrics.granger(dependent_series: pandas.core.series.Series, independent_series: pandas.core.series.Series, lags: int = 3, confidence_level: float = 0.05, export: str = '', chart=True)

Show granger tests

    Parameters
    ----------
    dependent_series: Series
        The series you want to test Granger Causality for.
    independent_series: Series
        The series that you want to test whether it Granger-causes dependent_series
    lags : int
        The amount of lags for the Granger test. By default, this is set to 3.
    confidence_level: float
        The confidence level you wish to use. By default, this is set to 0.05.
    export : str
        Format to export data
