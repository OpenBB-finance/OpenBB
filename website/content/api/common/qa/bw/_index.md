To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### common.qa.bw(data: pandas.core.frame.DataFrame, target: str, symbol: str = '', yearly: bool = True, external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None) -> None

Show box and whisker plots

    Parameters
    ----------
    symbol : str
        Name of dataset
    data : pd.DataFrame
        Dataframe to look at
    target : str
        Data column to look at
    yearly : bool
        Flag to indicate yearly accumulation
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None

## Getting charts 
### common.qa.bw(data: pandas.core.frame.DataFrame, target: str, symbol: str = '', yearly: bool = True, external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, chart=True) -> None

Show box and whisker plots

    Parameters
    ----------
    symbol : str
        Name of dataset
    data : pd.DataFrame
        Dataframe to look at
    target : str
        Data column to look at
    yearly : bool
        Flag to indicate yearly accumulation
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
