To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### crypto.tools.apy(apr: float, compounding_times: int) -> Tuple[pandas.core.frame.DataFrame, str]

Converts apr into apy

    Parameters
    ----------
    apr: float
        value in percentage
    compounding_times: int
        number of compounded periods in a year

    Returns
    -------
    Tuple:
        - pd.DataFrame: dataframe with results
        - str: narrative version of results

## Getting charts 
### crypto.tools.apy(apr: float, compounding_times: int, narrative: bool = False, export: str = '', chart=True)

Displays APY value converted from APR

    Parameters
    ----------
    apr: float
        value in percentage
    compounding_times: int
        number of compounded periods in a year
    narrative: str
        display narrative version instead of dataframe
    export : str
        Export dataframe data to csv,json,xlsx file

    Returns
    -------
