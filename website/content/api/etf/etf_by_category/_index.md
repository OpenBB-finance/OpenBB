To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### etf.etf_by_category(category: str) -> Dict

Return a selection of ETFs based on category filtered by total assets.
    [Source: Finance Database]

    Parameters
    ----------
    category: str
        Search by category to find ETFs matching the criteria.

    Returns
    ----------
    data : Dict
        Dictionary with ETFs that match a certain description

## Getting charts 
### etf.etf_by_category(category: str, limit: int = 10, export: str = '', chart=True)

Display a selection of ETFs based on a category filtered by total assets.
    [Source: Finance Database]

    Parameters
    ----------
    description: str
        Search by description to find ETFs matching the criteria.
    limit: int
        Limit of ETFs to display
    export: str
        Type of format to export data
