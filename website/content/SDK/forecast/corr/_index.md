To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### forecast.corr(data: pandas.core.frame.DataFrame) -> pandas.core.frame.DataFrame

Returns correlation for a given df

    Parameters
    ----------
    data: pd.DataFrame
        The df to produce statistics for

    Returns
    ----------
    df: pd.DataFrame
        The df with the new data

## Getting charts 
### forecast.corr(dataset: pandas.core.frame.DataFrame, export: str = '', external_axes: Optional[List[axes]] = None, chart=True)

Plot correlation coefficients for dataset features

    Parameters
    ----------
    dataset : pd.DataFrame
        The dataset fore calculating correlation coefficients
    export: str
        Format to export image
    external_axes:Optional[List[plt.axes]]
        External axes to plot on
