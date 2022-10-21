To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### stocks.options.screen.screener_output(preset: str) -> Tuple[pandas.core.frame.DataFrame, str]

Screen options based on preset filters

    Parameters
    ----------
    preset: str
        Chosen preset
    Returns
    -------
    pd.DataFrame:
        DataFrame with screener data, or empty if errors
    str:
        String containing error message if supplied

## Getting charts 
### stocks.options.screen.screener_output(preset: str, limit: int = 20, export: str = '', chart=True) -> List

Print the output of screener

    Parameters
    ----------
    preset: str
        Chosen preset
    limit: int
        Number of randomly sorted rows to display
    export: str
        Format for export file

    Returns
    -------
    List
        List of tickers screened
