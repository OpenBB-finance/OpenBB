## Get underlying data 
### crypto.disc.coins_for_given_exchange(exchange_id: str = 'binance', page: int = 1) -> dict

Helper method to get all coins available on binance exchange [Source: CoinGecko]

    Parameters
    ----------
    exchange_id: str
        id of exchange
    page: int
        number of page. One page contains 100 records

    Returns
    -------
    dict
        dictionary with all trading pairs on binance
