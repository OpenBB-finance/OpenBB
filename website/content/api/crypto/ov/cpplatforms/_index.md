To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### crypto.ov.cpplatforms() -> pandas.core.frame.DataFrame

List all smart contract platforms like ethereum, solana, cosmos, polkadot, kusama ... [Source: CoinPaprika]

    Returns
    -------
    pandas.DataFrame
        index, platform_id

## Getting charts 
### crypto.ov.cpplatforms(export: str, chart=True) -> None

List all smart contract platforms like ethereum, solana, cosmos, polkadot, kusama.
    [Source: CoinPaprika]

    Parameters
    ----------
    export : str
        Export dataframe data to csv,json,xlsx file
