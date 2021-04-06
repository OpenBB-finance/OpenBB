from unittest import mock, TestCase
from gamestonk_terminal.cryptocurrency.coin_api import load

# pylint: disable=unused-import


class TestCoinGeckoAPI(TestCase):
    @mock.patch(
        "gamestonk_terminal.cryptocurrency.coin_api.CoinGeckoAPI.get_coin_market_chart_by_id"
    )
    def test_coin_api_load(self, mock_load):
        coin, _ = load(["-c", "bitcoin"])
        self.assertEqual(coin, "bitcoin")
        self.assertTrue(mock_load.called)
