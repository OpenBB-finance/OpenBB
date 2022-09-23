To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### crypto.ov.cgglobal() -> pandas.core.frame.DataFrame

Get global statistics about crypto markets from CoinGecko API like:
        Market_Cap, Volume, Market_Cap_Percentage

    [Source: CoinGecko]

    Returns
    -------
    pandas.DataFrame
        Market_Cap, Volume, Market_Cap_Percentage

## Getting charts 
### crypto.ov.cgglobal(pie: bool = False, export: str = '', chart=True) -> None

Shows global statistics about crypto. [Source: CoinGecko]
        - market cap change
        - number of markets
        - icos
        - number of active crypto
        - market_cap_pct

    Parameters
    ----------
    pie: bool
        Whether to show a pie chart
    export : str
        Export dataframe data to csv,json,xlsx file
