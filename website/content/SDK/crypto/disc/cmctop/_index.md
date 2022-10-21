To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### crypto.disc.cmctop(sortby: str = 'CMC_Rank', ascend: bool = True) -> pandas.core.frame.DataFrame

Shows top n coins. [Source: CoinMarketCap]

    Parameters
    ----------
    sortby: str
        Key to sort data. The table can be sorted by every of its columns. Refer to
        Coin Market Cap:s API documentation, see:
        https://coinmarketcap.com/api/documentation/v1/#operation/getV1CryptocurrencyListingsLatest
    ascend: bool
        Whether to sort ascending or descending

    Returns
    -------
    pd.DataFrame
        Top coin on CoinMarketCap


## Getting charts 
### crypto.disc.cmctop(limit: int = 15, sortby: str = 'CMC_Rank', ascend: bool = True, export: str = '', chart=True) -> None

Shows top n coins. [Source: CoinMarketCap]

    Parameters
    ----------
    limit: int
        Number of records to display
    sortby: str
        Key to sort data. The table can be sorted by every of its columns. Refer to
        Coin Market Cap:s API documentation, see:
        https://coinmarketcap.com/api/documentation/v1/#operation/getV1CryptocurrencyListingsLatest
    ascend: bool
        Flag to sort data ascending
    export : str
        Export dataframe data to csv,json,xlsx file

