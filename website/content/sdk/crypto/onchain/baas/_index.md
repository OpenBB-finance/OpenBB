To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### crypto.onchain.baas(symbol: str = 'WETH', to_symbol: str = 'USDT', limit: int = 30, sortby: str = 'tradeAmount', ascend: bool = True) -> pandas.core.frame.DataFrame

Get an average bid and ask prices, average spread for given crypto pair for chosen time period.
       [Source: https://graphql.bitquery.io/]

    Parameters
    ----------
    limit:  int
        Last n days to query data
    symbol: str
        ERC20 token symbol
    to_symbol: str
        Quoted currency.
    sortby: str
        Key by which to sort data
    ascend: bool
        Flag to sort data ascending

    Returns
    -------
    pd.DataFrame
       Average bid and ask prices, spread for given crypto pair for chosen time period

## Getting charts 
### crypto.onchain.baas(symbol='ETH', to_symbol='USDC', days: int = 10, sortby: str = 'date', ascend: bool = True, export: str = '', chart=True) -> None

Display an average bid and ask prices, average spread for given crypto pair for chosen
    time period. [Source: https://graphql.bitquery.io/]

    Parameters
    ----------
    days:  int
        Last n days to query data
    symbol: str
        ERC20 token symbol
    to_symbol: str
        Quoted currency.
    sortby: str
        Key by which to sort data
    ascend: bool
        Flag to sort data ascending
    export : str
        Export dataframe data to csv,json,xlsx file

    Returns
    -------
    pd.DataFrame
        Average bid and ask prices, spread for given crypto pair for chosen time period
