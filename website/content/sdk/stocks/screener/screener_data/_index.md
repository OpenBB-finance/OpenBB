To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### stocks.screener.screener_data(preset_loaded: str = 'top_gainers', data_type: str = 'overview', limit: int = 10, ascend: bool = False)

Screener Overview

    Parameters
    ----------
    preset_loaded : str
        Loaded preset filter
    data_type : str
        Data type between: overview, valuation, financial, ownership, performance, technical
    limit : int
        Limit of stocks filtered with presets to print
    ascend : bool
        Ascended order of stocks filtered to print

    Returns
    ----------
    pd.DataFrame
        Dataframe with loaded filtered stocks

## Getting charts 
### stocks.screener.screener_data(loaded_preset: str = 'top_gainers', data_type: str = 'overview', limit: int = 10, ascend: bool = False, sortby: str = '', export: str = '', chart=True) -> List[str]

Screener one of the following: overview, valuation, financial, ownership, performance, technical.

    Parameters
    ----------
    loaded_preset: str
        Preset loaded to filter for tickers
    data_type : str
        Data type string between: overview, valuation, financial, ownership, performance, technical
    limit : int
        Limit of stocks to display
    ascend : bool
        Order of table to ascend or descend
    sortby: str
        Column to sort table by
    export : str
        Export dataframe data to csv,json,xlsx file

    Returns
    -------
    List[str]
        List of stocks that meet preset criteria
