# crypto.onchain.dvcp

To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
###crypto.onchain.dvcp(limit: int = 100, symbol: str = 'UNI', vs: str = 'USDT', sortby: str = 'date', ascend: bool = True) -> pandas.core.frame.DataFrame

Get daily volume for given pair [Source: https://graphql.bitquery.io/]

    Parameters
    -------
    limit:  int
        Last n days to query data
    symbol: str
        ERC20 token symbol
    vs: str
        Quote currency.
    sortby: str
        Key by which to sort data
    ascend: bool
        Flag to sort data ascending

    Returns
    -------
    pd.DataFrame
         Daily volume for given pair

## Getting charts 
###crypto.onchain.dvcp(symbol: str = 'WBTC', vs: str = 'USDT', top: int = 20, sortby: str = 'date', ascend: bool = True, export: str = '', chart=True) -> None

Display daily volume for given pair
    [Source: https://graphql.bitquery.io/]

    Parameters
    ----------
    symbol: str
        ERC20 token symbol or address
    vs: str
        Quote currency.
    top: int
        Number of records to display
    sortby: str
        Key by which to sort data
    ascend: bool
        Flag to sort data ascending
    export : str
        Export dataframe data to csv,json,xlsx file

    Returns
    -------
    pd.DataFrame
        Token volume on different decentralized exchanges
