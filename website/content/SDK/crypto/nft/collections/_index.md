To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### crypto.nft.collections() -> pandas.core.frame.DataFrame

Get nft collections [Source: https://nftpricefloor.com/]

    Parameters
    -------

    Returns
    -------
    pd.DataFrame
        nft collections

## Getting charts 
### crypto.nft.collections(show_fp: bool = False, show_sales: bool = False, limit: int = 5, export: str = '', chart=True)

Display NFT collections. [Source: https://nftpricefloor.com/]

    Parameters
    ----------
    show_fp : bool
        Show NFT Price Floor for top collections
    limit: int
        Number of NFT collections to display
    export : str
        Export dataframe data to csv,json,xlsx file
