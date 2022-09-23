# crypto.defi.newsletters

To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
###crypto.defi.newsletters() -> pandas.core.frame.DataFrame

Scrape all substack newsletters from url list.
    [Source: substack.com]

    Returns
    -------
    pd.DataFrame
        DataFrame with recent news from most popular DeFi related newsletters.

## Getting charts 
###crypto.defi.newsletters(top: int = 10, export: str = '', chart=True) -> None

Display DeFi related substack newsletters.
    [Source: substack.com]

    Parameters
    ----------
    top: int
        Number of records to display
    export : str
        Export dataframe data to csv,json,xlsx file
