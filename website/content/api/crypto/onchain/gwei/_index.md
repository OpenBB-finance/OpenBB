To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### crypto.onchain.gwei() -> pandas.core.frame.DataFrame

Returns the most recent Ethereum gas fees in gwei
    [Source: https://ethgasstation.info]

    Parameters
    ----------

    Returns
    -------
    pd.DataFrame
        four gas fees and durations
            (fees for slow, average, fast and
            fastest transactions in gwei and
            its average durations in seconds)

## Getting charts 
### crypto.onchain.gwei(export: str = '', chart=True) -> None

Current gwei fees
    [Source: https://ethgasstation.info]

    Parameters
    ----------
    export : str
        Export dataframe data to csv,json,xlsx file
