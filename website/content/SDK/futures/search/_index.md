To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### futures.search(category: str = '', exchange: str = '', description: str = '')

Get search futures [Source: Yahoo Finance]

    Parameters
    ----------
    category: str
        Select the category where the future exists
    exchange: str
        Select the exchange where the future exists
    description: str
        Select the description where the future exists

## Getting charts 
### futures.search(category: str = '', exchange: str = '', description: str = '', export: str = '', chart=True)

Display search futures [Source: Yahoo Finance]

    Parameters
    ----------
    category: str
        Select the category where the future exists
    exchange: str
        Select the exchange where the future exists
    description: str
        Select the description of the future
    export: str
        Type of format to export data
