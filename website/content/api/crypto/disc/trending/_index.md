To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### crypto.disc.trending() -> pandas.core.frame.DataFrame

Returns trending coins [Source: CoinGecko]

    Parameters
    ----------

    Returns
    -------
    pandas.DataFrame:
        Trending Coins

## Getting charts 
### crypto.disc.trending(export: str = '', chart=True) -> None

Display trending coins [Source: CoinGecko]

    Parameters
    ----------
    export : str
        Export dataframe data to csv,json,xlsx file
