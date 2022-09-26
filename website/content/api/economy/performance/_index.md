## Get underlying data 
### economy.performance(group: str = 'sector', sortby: str = 'Name', ascend: bool = True) -> pandas.core.frame.DataFrame

Get group (sectors, industry or country) performance data. [Source: Finviz]

    Parameters
    ----------
    group : str
       Group by category. Available groups can be accessed through get_groups().
    sortby : str
        Column to sort by
    ascend : bool
        Flag to sort in ascending order

    Returns
    ----------
    pd.DataFrame
        dataframe with performance data
