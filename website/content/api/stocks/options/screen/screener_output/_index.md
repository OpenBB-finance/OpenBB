# stocks.options.screen.screener_output

To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
###stocks.options.screen.screener_output(preset: str = 'high_IV', presets_path: str = '/Users/colindelahunty/OpenBBTerminal/openbb_terminal/stocks/options/screen/../presets/') -> Tuple[pandas.core.frame.DataFrame, str]

Screen options based on preset filters

    Parameters
    ----------
    preset: str
        Preset file to screen for
    presets_path: str
        Path to preset folder
    Returns
    -------
    pd.DataFrame:
        DataFrame with screener data, or empty if errors
    str:
        String containing error message if supplied

## Getting charts 
###stocks.options.screen.screener_output(preset: str = 'high_IV', presets_path: str = '/Users/colindelahunty/OpenBBTerminal/openbb_terminal/stocks/options/screen/../presets/', limit: int = 20, export: str = '', chart=True) -> List

Print the output of screener

    Parameters
    ----------
    preset: str
        Preset file to screen for
    presets_path: str
        Path to preset folder
    limit: int
        Number of randomly sorted rows to display
    export: str
        Format for export file

    Returns
    -------
    List
        List of tickers screened
