## Get underlying data 
### forecast.signal(dataset: pandas.core.frame.DataFrame, target_column: str = 'close') -> pandas.core.frame.DataFrame

A price signal based on short/long term price.

    1 if the signal is that short term price will go up as compared to the long term.
    0 if the signal is that short term price will go down as compared to the long term.

    Parameters
    ----------
    dataset : pd.DataFrame
        The dataset you wish to calculate with

    Returns
    -------
    pd.DataFrame:
        Dataframe with added signal column
