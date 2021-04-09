"""
Helper script that generates a dictionary to convert between symbols and IDs.
This allows the user to input (for example) "btc" instead of the expected "bitcoin"

"""
from pycoingecko import CoinGeckoAPI

cg = CoinGeckoAPI()
coins = cg.get_coins()
coin_symbol_to_id = {}
coin_ids = []

for coin in coins:
    coin_symbol_to_id[coin["symbol"]] = coin["id"]
    coin_ids.append(coin["id"])
