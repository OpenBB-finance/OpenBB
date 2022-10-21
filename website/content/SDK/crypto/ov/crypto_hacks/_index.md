To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### crypto.ov.crypto_hacks(sortby: str = 'Platform', ascend: bool = False) -> pandas.core.frame.DataFrame

Get major crypto-related hacks
    [Source: https://rekt.news]

    Parameters
    ----------
    sortby: str
        Key by which to sort data {Platform,Date,Amount [$],Audit,Slug,URL}
    ascend
        Flag to sort data ascending

    Returns
    -------
    pandas.DataFrame:
        Hacks with columns {Platform,Date,Amount [$],Audited,Slug,URL}

## Getting charts 
### crypto.ov.crypto_hacks(limit: int = 15, sortby: str = 'Platform', ascend: bool = False, slug: str = 'polyntwork-rekt', export: str = '', chart=True) -> None

Display list of major crypto-related hacks. If slug is passed
    individual crypto hack is displayed instead of list of crypto hacks
    [Source: https://rekt.news]

    Parameters
    ----------
    slug: str
        Crypto hack slug to check (e.g., polynetwork-rekt)
    limit: int
        Number of hacks to search
    sortby: str
        Key by which to sort data {Platform,Date,Amount [$],Audit,Slug,URL}
    ascend: bool
        Flag to sort data ascending
    export : str
        Export dataframe data to csv,json,xlsx file
