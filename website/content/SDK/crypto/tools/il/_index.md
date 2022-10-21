To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### crypto.tools.il(price_changeA: float, price_changeB: float, proportion: float, initial_pool_value: float) -> Tuple[pandas.core.frame.DataFrame, str]

Calculates Impermanent Loss in a custom liquidity pool

    Parameters
    ----------
    price_changeA: float
        price change of crypto A in percentage
    price_changeB: float
        price change of crypto B in percentage
    proportion: float
        percentage of first token in pool
    initial_pool_value: float
        initial value that pool contains

    Returns
    -------
    Tuple:
        - pd.DataFrame: dataframe with results
        - str: narrative version of results

## Getting charts 
### crypto.tools.il(price_changeA: int, price_changeB: int, proportion: int, initial_pool_value: int, narrative: bool = False, export: str = '', chart=True)

Displays Impermanent Loss in a custom liquidity pool

    Parameters
    ----------
    price_changeA: float
        price change of crypto A in percentage
    price_changeB: float
        price change of crypto B in percentage
    proportion: float
        percentage of first token in pool
    initial_pool_value: float
        initial value that pool contains
    narrative: str
        display narrative version instead of dataframe
    export : str
        Export dataframe data to csv,json,xlsx file

    Returns
    -------
