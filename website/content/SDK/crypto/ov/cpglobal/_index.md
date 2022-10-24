To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### crypto.ov.cpglobal() -> pandas.core.frame.DataFrame

Return data frame with most important global crypto statistics like:
    market_cap_usd, volume_24h_usd, bitcoin_dominance_percentage, cryptocurrencies_number,
    market_cap_ath_value, market_cap_ath_date, volume_24h_ath_value, volume_24h_ath_date,
    market_cap_change_24h, volume_24h_change_24h, last_updated.   [Source: CoinPaprika]

    Returns
    -------
    pandas.DataFrame
        Most important global crypto statistics
        Metric, Value

## Getting charts 
### crypto.ov.cpglobal(export: str = '', chart=True) -> None

Return data frame with most important global crypto statistics like:
    market_cap_usd, volume_24h_usd, bitcoin_dominance_percentage, cryptocurrencies_number,
    market_cap_ath_value, market_cap_ath_date, volume_24h_ath_value, volume_24h_ath_date,
    market_cap_change_24h, volume_24h_change_24h, last_updated [Source: CoinPaprika]

    Parameters
    ----------
    export : str
        Export dataframe data to csv,json,xlsx file
