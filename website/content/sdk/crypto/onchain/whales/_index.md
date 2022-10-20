To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### crypto.onchain.whales(min_value: int = 800000, limit: int = 100, sortby: str = 'date', ascend: bool = False) -> pandas.core.frame.DataFrame

Whale Alert's API allows you to retrieve live and historical transaction data from major blockchains.
    Supported blockchain: Bitcoin, Ethereum, Ripple, NEO, EOS, Stellar and Tron. [Source: https://docs.whale-alert.io/]

    Parameters
    ----------
    min_value: int
        Minimum value of trade to track.
    limit: int
        Limit of transactions. Max 100
    sortby: str
        Key to sort by.
    ascend: str
        Sort in ascending order.

    Returns
    -------
    pd.DataFrame
        Crypto wales transactions

## Getting charts 
### crypto.onchain.whales(min_value: int = 800000, limit: int = 100, sortby: str = 'date', ascend: bool = False, show_address: bool = False, export: str = '', chart=True) -> None

Display huge value transactions from major blockchains. [Source: https://docs.whale-alert.io/]

    Parameters
    ----------
    min_value: int
        Minimum value of trade to track.
    limit: int
        Limit of transactions. Maximum 100
    sortby: str
        Key to sort by.
    ascend: str
        Sort in ascending order.
    show_address: bool
        Flag to show addresses of transactions.
    export : str
        Export dataframe data to csv,json,xlsx file
