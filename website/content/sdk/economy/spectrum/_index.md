To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### economy.spectrum(group: str = 'sector')

Get group (sectors, industry or country) valuation/performance data. [Source: Finviz]

    Parameters
    ----------
    group : str
       Group by category. Available groups can be accessed through get_groups().

## Getting charts 
### economy.spectrum(group: str = 'sector', export: str = '', chart=True)

Display finviz spectrum in system viewer [Source: Finviz]

    Parameters
    ----------
    group: str
        Group by category. Available groups can be accessed through get_groups().
    export: str
        Format to export data
