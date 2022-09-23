To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### crypto.ov.cgdefi() -> pandas.core.frame.DataFrame

Get global statistics about Decentralized Finances [Source: CoinGecko]

    Returns
    -------
    pandas.DataFrame
        Metric, Value

## Getting charts 
### crypto.ov.cgdefi(export: str = '', chart=True) -> None

Shows global statistics about Decentralized Finances. [Source: CoinGecko]

    Parameters
    ----------
    export : str
        Export dataframe data to csv,json,xlsx file
