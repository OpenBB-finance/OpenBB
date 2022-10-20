To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### stocks.options.unu(limit: int = 100)

Get unusual option activity from fdscanner.com

    Parameters
    ----------
    limit: int
        Number to show

    Returns
    -------
    df: pd.DataFrame
        Dataframe containing options information
    last_updated: pd.Timestamp
        Timestamp indicated when data was updated from website

## Getting charts 
### stocks.options.unu(limit: int = 20, sortby: str = 'Vol/OI', ascend: bool = False, calls_only: bool = False, puts_only: bool = False, export: str = '', chart=True)

Displays the unusual options table

    Parameters
    ----------
    limit: int
        Number of rows to show
    sortby: str
        Data column to sort on
    ascend: bool
        Whether to sort in ascend order
    calls_only : bool
        Flag to only show calls
    puts_only : bool
        Flag to show puts only
    export: str
        File type to export
