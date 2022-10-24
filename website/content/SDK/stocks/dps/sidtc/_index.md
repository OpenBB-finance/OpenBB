## Get underlying data 
### stocks.dps.sidtc(sortby: str = 'float') -> pandas.core.frame.DataFrame

Get short interest and days to cover. [Source: Stockgrid]

    Parameters
    ----------
    sortby : str
        Field for which to sort by, where 'float': Float Short %%,
        'dtc': Days to Cover, 'si': Short Interest

    Returns
    ----------
    pd.DataFrame
        Short interest and days to cover data
