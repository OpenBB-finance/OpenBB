To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### crypto.disc.coins(limit: int = 250, category: str = '', sortby: str = 'Symbol', ascend: bool = False) -> pandas.core.frame.DataFrame

Get N coins from CoinGecko [Source: CoinGecko]

    Parameters
    ----------
    limit: int
        Number of top coins to grab from CoinGecko
    category: str
        Category of the coins we want to retrieve
    sortby: str
        Key to sort data
    ascend: bool
        Sort data in ascending order

    Returns
    -------
    pandas.DataFrame
        N coins

## Getting charts 
### crypto.disc.coins(category: str, limit: int = 250, sortby: str = 'Symbol', export: str = '', ascend: bool = False, chart=True) -> None

Display top coins [Source: CoinGecko]

    Parameters
    ----------
    category: str
        If no category is passed it will search for all coins. (E.g., smart-contract-platform)
    limit: int
        Number of records to display
    sortby: str
        Key to sort data
    export : str
        Export dataframe data to csv,json,xlsx file
    ascend: bool
        Sort data in ascending order
