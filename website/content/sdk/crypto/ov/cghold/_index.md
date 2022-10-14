To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### crypto.ov.cghold(endpoint: str = 'bitcoin') -> List[Any]

Returns public companies that holds ethereum or bitcoin [Source: CoinGecko]

    Parameters
    ----------
    endpoint : str
        "bitcoin" or "ethereum"

    Returns
    -------
    List:
        - str:              Overall statistics
        - pandas.DataFrame: Companies holding crypto

## Getting charts 
### crypto.ov.cghold(symbol: str, show_bar: bool = False, export: str = '', limit: int = 15, chart=True) -> None

Shows overview of public companies that holds ethereum or bitcoin. [Source: CoinGecko]

    Parameters
    ----------
    symbol: str
        Cryptocurrency: ethereum or bitcoin
    show_bar : bool
        Whether to show a bar graph for the data
    export: str
        Export dataframe data to csv,json,xlsx
    limit: int
        The number of rows to show
