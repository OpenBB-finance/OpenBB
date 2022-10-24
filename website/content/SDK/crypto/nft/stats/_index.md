To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### crypto.nft.stats(slug: str) -> pandas.core.frame.DataFrame

Get stats of a nft collection [Source: opensea.io]

    Parameters
    -------
    slug : str
        Opensea collection slug. If the name of the collection is Mutant Ape Yacht Club the slug is mutant-ape-yacht-club

    Returns
    -------
    pd.DataFrame
        collection stats

## Getting charts 
### crypto.nft.stats(slug: str, export: str, chart=True)

Display collection stats. [Source: opensea.io]

    Parameters
    ----------
    slug: str
        Opensea collection slug.
        If the name of the collection is Mutant Ape Yacht Club the slug is mutant-ape-yacht-club
    export : str
        Export dataframe data to csv,json,xlsx file
