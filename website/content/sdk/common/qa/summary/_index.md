To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### common.qa.summary(data: pandas.core.frame.DataFrame) -> pandas.core.frame.DataFrame

Print summary statistics

    Parameters
    ----------
    data : pd.DataFrame
        Dataframe to get summary statistics for

    Returns
    -------
    summary : pd.DataFrame
        Summary statistics

## Getting charts 
### common.qa.summary(data: pandas.core.frame.DataFrame, export: str = '', chart=True) -> None

Show summary statistics

    Parameters
    ----------
    data : pd.DataFrame
        DataFrame to get statistics of
    export : str
        Format to export data
