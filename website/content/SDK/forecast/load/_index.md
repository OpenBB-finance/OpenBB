## Get underlying data 
### forecast.load(file: str, data_files: Optional[Dict[Any, Any]] = None, data_examples: Optional[Dict[Any, Any]] = None) -> pandas.core.frame.DataFrame

Load custom file into dataframe.

    Parameters
    ----------
    file: str
        Path to file
    data_files: dict
        Contains all available data files within the Export folder
    data_examples: dict
        Contains all available examples from Statsmodels

    Returns
    -------
    pd.DataFrame:
        Dataframe with custom data
