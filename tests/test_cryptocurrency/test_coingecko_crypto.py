from unittest import mock, TestCase
import json
from pycoingecko import CoinGeckoAPI
from gamestonk_terminal.cryptocurrency.coingecko.pycoingecko_view import load, ta
from gamestonk_terminal.cryptocurrency.coingecko.pycoingecko_coin_model import Coin

# pylint: disable=unused-import


class TestCoinGeckoAPI(TestCase):
    @mock.patch(
        "gamestonk_terminal.cryptocurrency.coingecko.pycoingecko_view.CoinGeckoAPI.get_coin_market_chart_by_id"
    )
    def test_coin_api_load(self, mock_load):
        """
        Mock load function through get_coin_market_chart_by_id.
        Mock returns a dict saved as .json

        """
        with open("tests/data/btc_usd_test_data.json") as f:
            sample_return = json.load(f)

        mock_load.return_value = sample_return
        coin = load(["-c", "bitcoin"])
        self.assertEqual(coin.coin_symbol, "bitcoin")
        self.assertIsInstance(coin, Coin)

    @mock.patch(
        "gamestonk_terminal.cryptocurrency.coingecko.pycoingecko_view.CoinGeckoAPI.get_coin_market_chart_by_id"
    )
    def test_coin_api_load_df_for_ta(self, mock_load):
        """
        Mock load function through get_coin_market_chart_by_id.
        Mock returns a dict saved as .json

        """

        with open("tests/data/btc_usd_test_data.json") as f:
            sample_return = json.load(f)

        mock_load.return_value = sample_return
        coin = load(["-c", "bitcoin"])
        mock_return, vs = ta(coin, ["--vs", "usd"])
        self.assertTrue(mock_return.shape == (722, 2))
        self.assertTrue(vs == "usd")

    def test_coin(self):
        """Test that pycoingecko retrieves the major coins"""

        coins = CoinGeckoAPI().get_coins()
        coin_list = [coin["id"] for coin in coins]
        test_coins = ["bitcoin", "ethereum", "dogecoin"]
        for test in test_coins:
            self.assertIn(test, coin_list)
