## Get underlying data 
### economy.future(future_type: str = 'Indices', sortby: str = 'ticker', ascend: bool = False) -> pandas.core.frame.DataFrame

Get futures data. [Source: Finviz]

    Parameters
    ----------
    future_type : str
        From the following: Indices, Energy, Metals, Meats, Grains, Softs, Bonds, Currencies
    sortby : str
        Column to sort by
    ascend : bool
        Flag to sort in ascending order

    Returns
    ----------
    pd.Dataframe
       Indices, Energy, Metals, Meats, Grains, Softs, Bonds, Currencies
