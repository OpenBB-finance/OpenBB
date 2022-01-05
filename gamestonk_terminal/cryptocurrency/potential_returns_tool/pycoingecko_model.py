"""CoinGecko model"""
__docformat__ = "numpy"

from pycoingecko import CoinGeckoAPI


def get_coins_data(self, coin1: str, coin2: str):
    """[Source: CoinGecko]

    Parameters
    ----------

    Returns
    -------

    """
    client = CoinGeckoAPI()
