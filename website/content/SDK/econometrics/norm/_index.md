To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### econometrics.norm(data: pandas.core.series.Series) -> pandas.core.frame.DataFrame


    The distribution of returns and generate statistics on the relation to the normal curve.
    This function calculates skew and kurtosis (the third and fourth moments) and performs both
    a Jarque-Bera and Shapiro Wilk test to determine if data is normally distributed.

    Parameters
    ----------
    data : pd.Series
        A series or column of a DataFrame to test normality for

    Returns
    -------
    pd.DataFrame
        Dataframe containing statistics of normality

## Getting charts 
### econometrics.norm(data: pandas.core.series.Series, dataset: str = '', column: str = '', plot: bool = False, export: str = '', external_axes: Optional[List[axes]] = None, chart=True)

Determine the normality of a timeseries.

    Parameters
    ----------
    data: pd.Series
        Series of custom data
    dataset: str
        Dataset name
    column: str
        Column for y data
    plot : bool
        Whether you wish to plot a histogram
    export: str
        Format to export data.
    external_axes: Optional[List[plt.axes]]
        External axes to plot on
