To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### forecast.plot(data: Union[pandas.core.frame.DataFrame, Dict[str, pandas.core.frame.DataFrame]], export: str = '', external_axes: Optional[List[axes]] = None)

Plot data from a dataset
    Parameters
    ----------
    data: Dict[str: pd.DataFrame]
        Dictionary with key being dataset.column and dataframes being values
    export: str
        Format to export image
    external_axes:Optional[List[plt.axes]]
        External axes to plot on

## Getting charts 
### forecast.plot(data: Union[pandas.core.frame.DataFrame, Dict[str, pandas.core.frame.DataFrame]], export: str = '', external_axes: Optional[List[axes]] = None, chart=True)

Plot data from a dataset
    Parameters
    ----------
    data: Dict[str: pd.DataFrame]
        Dictionary with key being dataset.column and dataframes being values
    export: str
        Format to export image
    external_axes:Optional[List[plt.axes]]
        External axes to plot on
