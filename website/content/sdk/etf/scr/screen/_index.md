To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### etf.scr.screen(preset: str)


    Screens the etfs pulled from my repo (https://github.com/jmaslek/etf_scraper),
    which is updated hourly through the market day

    Parameters
    ----------
    preset: str
        Screener to use from presets

    Returns
    ----------
    df : pd.DataFrame
        Screened dataframe

## Getting charts 
### etf.scr.screen(preset: str, num_to_show: int, sortby: str, ascend: bool, export: str = '', chart=True)

Display screener output

    Parameters
    ----------
    preset: str
        Preset to use
    num_to_show: int
        Number of etfs to show
    sortby: str
        Column to sort by
    ascend: bool
        Ascend when sorted
    export: str
        Output format of export

