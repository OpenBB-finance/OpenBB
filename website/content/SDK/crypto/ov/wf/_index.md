To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### crypto.ov.wf(limit: int = 100) -> pandas.core.frame.DataFrame

Scrapes top coins withdrawal fees
    [Source: https://withdrawalfees.com/]

    Parameters
    ----------
    limit: int
        Number of coins to search, by default n=100, one page has 100 coins, so 1 page is scraped.
    Returns
    -------
    pandas.DataFrame:
        Coin, Lowest, Average, Median, Highest, Exchanges Compared

## Getting charts 
### crypto.ov.wf(limit: int = 15, export: str = '', chart=True) -> None

Top coins withdrawal fees
    [Source: https://withdrawalfees.com/]

    Parameters
    ----------
    limit: int
        Number of coins to search
    export : str
        Export dataframe data to csv,json,xlsx file
