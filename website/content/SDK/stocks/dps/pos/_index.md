## Get underlying data 
### stocks.dps.pos(sortby: str = 'dpp_dollar', ascend: bool = False) -> pandas.core.frame.DataFrame

Get dark pool short positions. [Source: Stockgrid]

    Parameters
    ----------
    sortby : str
        Field for which to sort by, where 'sv': Short Vol. [1M],
        'sv_pct': Short Vol. %%, 'nsv': Net Short Vol. [1M],
        'nsv_dollar': Net Short Vol. ($100M), 'dpp': DP Position [1M],
        'dpp_dollar': DP Position ($1B)
    ascend : bool
        Data in ascending order

    Returns
    ----------
    pd.DataFrame
        Dark pool short position data
