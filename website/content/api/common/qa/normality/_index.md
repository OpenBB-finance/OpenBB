To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### common.qa.normality(data: pandas.core.frame.DataFrame) -> pandas.core.frame.DataFrame


    Look at the distribution of returns and generate statistics on the relation to the normal curve.
    This function calculates skew and kurtosis (the third and fourth moments) and performs both
    a Jarque-Bera and Shapiro Wilk test to determine if data is normally distributed.

    Parameters
    ----------
    data : pd.DataFrame
        Dataframe of targeted data

    Returns
    -------
    pd.DataFrame
        Dataframe containing statistics of normality

## Getting charts 
### common.qa.normality(data: pandas.core.frame.DataFrame, target: str, export: str = '', chart=True) -> None

View normality statistics

    Parameters
    ----------
    data : pd.DataFrame
        DataFrame
    target : str
        Column in data to look at
    export : str
        Format to export data
