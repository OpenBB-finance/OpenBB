To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### crypto.disc.top_nfts(sortby: str = '', limit: int = 10) -> pandas.core.frame.DataFrame

Get top nft collections [Source: https://dappradar.com/]

    Parameters
    ----------
    sortby: str
        Key by which to sort data

    Returns
    -------
    pd.DataFrame
        NFTs Columns: Name, Protocols, Floor Price [$], Avg Price [$], Market Cap [$], Volume [$]

## Getting charts 
### crypto.disc.top_nfts(limit: int = 10, sortby: str = '', export: str = '', chart=True) -> None

Displays top nft collections [Source: https://dappradar.com/]

    Parameters
    ----------
    limit: int
        Number of records to display
    sortby: str
        Key by which to sort data
    export : str
        Export dataframe data to csv,json,xlsx file
