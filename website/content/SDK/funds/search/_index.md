To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### funds.search(by: str = 'name', value: str = '') -> pandas.core.frame.DataFrame

Search investpy for matching funds

    Parameters
    ----------
    by : str
        Field to match on.  Can be name, issuer, isin or symbol
    value : str
        String that will be searched for

    Returns
    -------
    pd.DataFrame
        Dataframe containing matches

## Getting charts 
### funds.search(by: str = 'name', value: str = '', country: str = 'united states', limit: int = 10, sortby: str = '', ascend: bool = False, chart=True)

Display results of searching for Mutual Funds

    Parameters
    ----------
    by : str
        Field to match on.  Can be name, issuer, isin or symbol
    value : str
        String that will be searched for
    country: str
        Country to filter on
    limit: int
        Number to show
    sortby: str
        Column to sort by
    ascend: bool
        Flag to sort in ascending order
