To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### crypto.nft.fp(slug) -> pandas.core.frame.DataFrame

Get nft collections [Source: https://nftpricefloor.com/]

    Parameters
    -------
    slug: str
        nft collection slug

    Returns
    -------
    pd.DataFrame
        nft collections

## Getting charts 
### crypto.nft.fp(slug: str, limit: int = 10, export: str = '', external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, raw: bool = False, chart=True)

Display NFT collection floor price over time. [Source: https://nftpricefloor.com/]

    Parameters
    ----------
    slug: str
        NFT collection slug
    raw: bool
        Flag to display raw data
    limit: int
        Number of raw data to show
    export: str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (2 axes are expected in the list), by default None
