## Get underlying data 
### stocks.ca.finviz_peers(symbol: str, compare_list: List[str] = None) -> Tuple[List[str], str]

Get similar companies from Finviz

    Parameters
    ----------
    symbol : str
        Ticker to find comparisons for
    compare_list : List[str]
        List of fields to compare, ["Sector", "Industry", "Country"]

    Returns
    -------
    List[str]
        List of similar companies
