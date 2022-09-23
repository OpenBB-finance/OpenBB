To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### crypto.ov.cgderivatives(sortby: str = 'Rank', ascend: bool = False) -> pandas.core.frame.DataFrame

Get list of crypto derivatives from CoinGecko API [Source: CoinGecko]

    Parameters
    ----------
    sortby: str
        Key by which to sort data
    ascend: bool
        Flag to sort data descending

    Returns
    -------
    pandas.DataFrame
        Rank, Market, Symbol, Price, Pct_Change_24h, Contract_Type, Basis, Spread,
        Funding_Rate, Volume_24h,

## Getting charts 
### crypto.ov.cgderivatives(sortby: str = 'Rank', ascend: bool = False, limit: int = 15, export: str = '', chart=True) -> None

Shows  list of crypto derivatives. [Source: CoinGecko]

    Parameters
    ----------
    limit: int
        Number of records to display
    sortby: str
        Key by which to sort data
    ascend: bool
        Flag to sort data descending
    export : str
        Export dataframe data to csv,json,xlsx file
