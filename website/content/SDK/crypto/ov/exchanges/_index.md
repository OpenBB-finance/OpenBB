To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### crypto.ov.exchanges(sortby: str = 'name', ascend: bool = False) -> pandas.core.frame.DataFrame

Get list of top exchanges from CoinGecko API [Source: CoinGecko]

    Parameters
    ----------
    sortby: str
        Key by which to sort data
    ascend: bool
        Flag to sort data descending

    Returns
    -------
    pandas.DataFrame
        Trust_Score, Id, Name, Country, Year_Established, Trade_Volume_24h_BTC, Url

## Getting charts 
### crypto.ov.exchanges(sortby: str = 'name', ascend: bool = False, limit: int = 15, links: bool = False, export: str = '', chart=True) -> None

Shows list of top exchanges from CoinGecko. [Source: CoinGecko]

    Parameters
    ----------
    limit: int
        Number of records to display
    sortby: str
        Key by which to sort data
    ascend: bool
        Flag to sort data descending
    links: bool
        Flag to display urls
    export : str
        Export dataframe data to csv,json,xlsx file
