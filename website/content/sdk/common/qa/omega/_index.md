To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### common.qa.omega(data: pandas.core.frame.DataFrame, threshold_start: float = 0, threshold_end: float = 1.5) -> pandas.core.frame.DataFrame

Get the omega series
    Parameters
    ----------
    data: pd.DataFrame
        stock dataframe
    threshold_start: float
        annualized target return threshold start of plotted threshold range
    threshold_end: float
        annualized target return threshold end of plotted threshold range

## Getting charts 
### common.qa.omega(data: pandas.core.frame.DataFrame, threshold_start: float = 0, threshold_end: float = 1.5, chart=True) -> None

Displays the omega ratio
    Parameters
    ----------
    data: pd.DataFrame
        stock dataframe
    threshold_start: float
        annualized target return threshold start of plotted threshold range
    threshold_end: float
        annualized target return threshold end of plotted threshold range
