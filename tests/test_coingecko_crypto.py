from unittest import mock, TestCase
import json
from pycoingecko import CoinGeckoAPI
from gamestonk_terminal.cryptocurrency.coin_api import load

# pylint: disable=unused-import


class TestCoinGeckoAPI(TestCase):
    @mock.patch(
        "gamestonk_terminal.cryptocurrency.coin_api.CoinGeckoAPI.get_coin_market_chart_by_id"
    )
    def test_coin_api_load(self, mock_load):
        """
        Mock load function through get_coin_market_chart_by_id.
        Mock returns a dict saved as .json

        """
        with open("tests/data/btc_usd_test_data.json") as f:
            sample_return = json.load(f)

        mock_load.return_value = sample_return
        coin, mock_return = load(["-c", "bitcoin"])
        self.assertEqual(coin, "bitcoin")
        self.assertTrue(mock_load.called)
        self.assertTrue(mock_return.shape == (722, 2))

    def test_coin(self):
        """Test that pycoingecko retrieves the major coins"""

        coins = CoinGeckoAPI().get_coins()
        coin_list = [coin["id"] for coin in coins]
        test_coins = ["bitcoin", "ethereum", "dogecoin"]
        for test in test_coins:
            self.assertIn(test, coin_list)
