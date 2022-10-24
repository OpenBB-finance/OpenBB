## Get underlying data 
### stocks.disc.arkord(sortby: str = '', ascend: bool = False, buys_only: bool = False, sells_only: bool = False, fund: str = '') -> pandas.core.frame.DataFrame

Returns ARK orders in a Dataframe

    Parameters
    ----------
    sortby: str
        Column to sort on
    ascend: bool
        Flag to sort in ascending order
    buys_only: bool
        Flag to filter on buys only
    sells_only: bool
        Flag to sort on sells only
    fund: str
        Optional filter by fund

    Returns
    -------
    DataFrame
        ARK orders data frame with the following columns:
        ticker, date, shares, weight, fund, direction
