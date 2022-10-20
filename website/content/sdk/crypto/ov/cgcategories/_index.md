To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### crypto.ov.cgcategories(sort_filter: str = 'market_cap_desc') -> pandas.core.frame.DataFrame

Returns top crypto categories [Source: CoinGecko]

    Returns
    -------
    pandas.DataFrame
       Rank, Name, Change_1h, Change_7d, Market_Cap, Volume_24h,Coins, Url

## Getting charts 
### crypto.ov.cgcategories(sortby: str = 'market_cap_desc', limit: int = 15, export: str = '', pie: bool = False, chart=True) -> None

Shows top cryptocurrency categories by market capitalization

    The cryptocurrency category ranking is based on market capitalization. [Source: CoinGecko]

    Parameters
    ----------
    sortby: str
        Key by which to sort data
    limit: int
        Number of records to display
    export: str
        Export dataframe data to csv,json,xlsx file
    pie: bool
        Whether to show the pie chart
