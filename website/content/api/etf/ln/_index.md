To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### etf.ln(name: str) -> Dict

Return a selection of ETFs based on name filtered by total assets. [Source: Finance Database]

    Parameters
    ----------
    name: str
        Search by name to find ETFs matching the criteria.

    Returns
    ----------
    data : Dict
        Dictionary with ETFs that match a certain name

## Getting charts 
### etf.ln(name: str, limit: int = 10, export: str = '', chart=True)

Display a selection of ETFs based on name filtered by total assets. [Source: Finance Database]

    Parameters
    ----------
    name: str
        Search by name to find ETFs matching the criteria.
    limit: int
        Limit of ETFs to display
    export: str
        Type of format to export data
