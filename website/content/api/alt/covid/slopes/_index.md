To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### alt.covid.slopes(days_back: int = 30, limit: int = 50, threshold: int = 10000, ascend: bool = False) -> pandas.core.frame.DataFrame

Load cases and find slope over period

    Parameters
    ----------
    days_back: int
        Number of historical days to consider
    limit: int
        Number of rows to show
    threshold: int
        Threshold for total number of cases
    ascend: bool
        Flag to sort in ascending order
    Returns
    -------
    pd.DataFrame
        Dataframe containing slopes

## Getting charts 
### alt.covid.slopes(days_back: int = 30, limit: int = 10, threshold: int = 10000, ascend: bool = False, export: str = '', chart=True) -> None



    Parameters
    ----------
    days_back: int
        Number of historical days to get slope for
    limit: int
        Number to show in table
    ascend: bool
        Flag to sort in ascending order
    threshold: int
        Threshold for total cases over period
    export : str
        Format to export data
