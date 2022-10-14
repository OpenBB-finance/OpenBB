# alt.covid.case_slopes

## Get underlying data 
###alt.covid.case_slopes(days_back: int = 30, threshold: int = 10000) -> pandas.core.frame.DataFrame

Load cases and find slope over period

    Parameters
    ----------
    days_back: int
        Number of historical days to consider
    threshold: int
        Threshold for total number of cases
    Returns
    -------
    pd.DataFrame
        Dataframe containing slopes
