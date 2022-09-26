To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### crypto.ov.ewf() -> pandas.core.frame.DataFrame

Scrapes exchange withdrawal fees
    [Source: https://withdrawalfees.com/]

    Parameters
    ----------

    Returns
    -------
    pandas.DataFrame:
        Exchange, Coins, Lowest, Average, Median, Highest

## Getting charts 
### crypto.ov.ewf(export: str = '', chart=True) -> None

Exchange withdrawal fees
    [Source: https://withdrawalfees.com/]

    Parameters
    ----------
    export : str
        Export dataframe data to csv,json,xlsx file
