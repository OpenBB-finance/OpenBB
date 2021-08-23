from unittest import mock, TestCase
import json
import os

import vcr
from pycoingecko import CoinGeckoAPI
from gamestonk_terminal.cryptocurrency.overview import (
    pycoingecko_view as ov_pycoingecko_view,
)
from gamestonk_terminal.cryptocurrency.due_diligence import (
    pycoingecko_view as dd_pycoingecko_view,
)
from gamestonk_terminal.cryptocurrency.discovery import (
    pycoingecko_view as disc_pycoingecko_view,
)

from gamestonk_terminal.cryptocurrency.due_diligence.pycoingecko_model import Coin

from tests.helpers import check_print

# pylint: disable=unused-import


@mock.patch(
    "gamestonk_terminal.cryptocurrency.due_diligence.pycoingecko_model.CoinGeckoAPI.get_coin_market_chart_by_id"
)
def get_bitcoin(mock_load):
    # pylint: disable=unused-argument
    print(os.getcwd())
    with open("tests/data/btc_usd_test_data.json", encoding="utf8") as f:
        sample_return = json.load(f)
    mock_load.return_value = sample_return
    return dd_pycoingecko_view.load(["-c", "bitcoin"])


# pylint: disable=R0904
class TestCoinGeckoAPI(TestCase):
    # pylint: disable = no-value-for-parameter
    coin = get_bitcoin()

    def test_coin_api_load(self):
        """
        Mock load function through get_coin_market_chart_by_id.
        Mock returns a dict saved as .json
        """
        self.assertEqual(self.coin.coin_symbol, "bitcoin")
        self.assertIsInstance(self.coin, Coin)

    @mock.patch(
        "gamestonk_terminal.cryptocurrency.due_diligence.pycoingecko_model.CoinGeckoAPI.get_coin_market_chart_by_id"
    )
    def test_coin_api_load_df_for_ta(self, mock_load):
        """
        Mock load function through get_coin_market_chart_by_id.
        Mock returns a dict saved as .json
        """

        with open("tests/data/btc_usd_test_data.json", encoding="utf8") as f:
            sample_return = json.load(f)

        mock_load.return_value = sample_return
        mock_return, vs = dd_pycoingecko_view.load_ta_data(
            self.coin, ["--vs", "usd", "--days", "30"]
        )
        self.assertTrue(mock_return.shape == (31, 4))
        self.assertTrue(vs == "usd")

    @check_print()
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coingecko/test_get_coins.yaml",
        record_mode="new_episodes",
    )
    def test_get_coins(self):
        """Test that pycoingecko retrieves the major coins"""
        coins = CoinGeckoAPI().get_coins()
        bitcoin_list = [coin["id"] for coin in coins]
        test_coins = ["bitcoin", "ethereum", "dogecoin"]
        for test in test_coins:
            self.assertIn(test, bitcoin_list)

    @check_print(assert_in="\n")
    @mock.patch("matplotlib.pyplot.show")
    def test_coin_chart(self, mock_matplot):
        # pylint: disable=unused-argument
        dd_pycoingecko_view.chart(self.coin, [])

    @check_print(assert_in="Market Cap Rank")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coingecko/test_coin_info.yaml",
        record_mode="new_episodes",
    )
    def test_coin_info(self):
        dd_pycoingecko_view.info(self.coin, [])

    @check_print(assert_in="Homepage")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coingecko/test_coin_web.yaml",
        record_mode="new_episodes",
    )
    def test_coin_web(self):
        dd_pycoingecko_view.web(self.coin, [])

    @check_print(assert_in="Metric")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coingecko/test_coin_social.yaml",
        record_mode="new_episodes",
    )
    def test_coin_social(self):
        dd_pycoingecko_view.social(self.coin, [])

    @check_print(assert_in="Metric")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coingecko/test_coin_dev.yaml",
        record_mode="new_episodes",
    )
    def test_coin_dev(self):
        dd_pycoingecko_view.dev(self.coin, [])

    @check_print(assert_in="Metric")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coingecko/test_coin_ath.yaml",
        record_mode="new_episodes",
    )
    def test_coin_ath(self):
        dd_pycoingecko_view.ath(self.coin, [])

    @check_print(assert_in="Metric")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coingecko/test_coin_atl.yaml",
        record_mode="new_episodes",
    )
    def test_coin_atl(self):
        dd_pycoingecko_view.atl(self.coin, [])

    @check_print(assert_in="Metric")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coingecko/test_coin_score.yaml",
        record_mode="new_episodes",
    )
    def test_coin_score(self):
        dd_pycoingecko_view.score(self.coin, [])

    @check_print(assert_in="Metric")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coingecko/test_coin_bc.yaml",
        record_mode="new_episodes",
    )
    def test_coin_bc(self):
        dd_pycoingecko_view.bc(self.coin, [])

    @check_print(assert_in="Metric")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coingecko/test_coin_market.yaml",
        record_mode="new_episodes",
    )
    def test_coin_market(self):
        dd_pycoingecko_view.market(self.coin, [])

    @check_print(assert_in="Total Bitcoin Holdings")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coingecko/test_coin_overview.yaml",
        record_mode="new_episodes",
    )
    def test_coin_holdings_overview(self):
        ov_pycoingecko_view.holdings_overview([])

    @check_print(assert_in="═══════")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coingecko/test_coin_holding_comapnies.yaml",
        record_mode="new_episodes",
    )
    def test_coin_holdings_companies_list(self):
        ov_pycoingecko_view.holdings_companies_list([])

    @check_print(assert_in="Rank")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coingecko/test_coin_gainers.yaml",
        record_mode="new_episodes",
    )
    def test_coin_gainers(self):
        disc_pycoingecko_view.gainers([])

    @check_print(assert_in="Rank")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coingecko/test_coin_losers.yaml",
        record_mode="new_episodes",
    )
    def test_coin_losers(self):
        disc_pycoingecko_view.losers([])

    @check_print(assert_in="CryptoBlades")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coingecko/test_coin_discover.yaml",
        record_mode="new_episodes",
    )
    def test_coin_discover(self):
        disc_pycoingecko_view.discover("trending", [])

    @check_print(assert_in="═════════════")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coingecko/test_coin_news.yaml",
        record_mode="new_episodes",
    )
    def test_coin_news(self):
        ov_pycoingecko_view.news([])

    @check_print(assert_in="Decentralized Finance")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coingecko/test_coin_categories.yaml",
        record_mode="new_episodes",
    )
    def test_coin_categories(self):
        ov_pycoingecko_view.categories([])

    @check_print(assert_in="════════")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coingecko/test_coin_recently_added.yaml",
        record_mode="new_episodes",
    )
    def test_coin_recently_added(self):
        disc_pycoingecko_view.recently_added([])

    @check_print(assert_in="════")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coingecko/test_coin_stablecoins.yaml",
        record_mode="new_episodes",
    )
    def test_coin_stablecoins(self):
        ov_pycoingecko_view.stablecoins([])

    @check_print(assert_in="════════")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coingecko/test_coin_yfarms.yaml",
        record_mode="new_episodes",
    )
    def test_coin_yfarms(self):
        disc_pycoingecko_view.yfarms([])

    @check_print(assert_in="════════")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coingecko/test_coin_top_volume_coins.yaml",
        record_mode="new_episodes",
    )
    def test_coin_top_volume_coins(self):
        disc_pycoingecko_view.top_volume_coins([])

    @check_print(assert_in="═════════")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coingecko/test_coin_top_defi_coins.yaml",
        record_mode="new_episodes",
    )
    def test_coin_top_defi_coins(self):
        disc_pycoingecko_view.top_defi_coins([])

    @check_print(assert_in="════════")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coingecko/test_coin_top_dex.yaml",
        record_mode="new_episodes",
    )
    def test_coin_top_dex(self):
        disc_pycoingecko_view.top_dex([])

    @check_print(assert_in="Metric")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coingecko/test_coin_nft_market-status.yaml",
        record_mode="new_episodes",
    )
    def test_coin_nft_market_status(self):
        ov_pycoingecko_view.nft_market_status([])

    @check_print(assert_in="═══════════")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coingecko/test_coin_exchanges.yaml",
        record_mode="new_episodes",
    )
    def test_coin_exchanges(self):
        ov_pycoingecko_view.exchanges([])

    @check_print(assert_in="Rank")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coingecko/test_coin_platforms.yaml",
        record_mode="new_episodes",
    )
    def test_coin_platforms(self):
        ov_pycoingecko_view.platforms([])

    @check_print(assert_in="Rank")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coingecko/test_coin_products.yaml",
        record_mode="new_episodes",
    )
    def test_coin_products(self):
        ov_pycoingecko_view.products([])

    @check_print(assert_in="Rank")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coingecko/test_coin_indexes.yaml",
        record_mode="new_episodes",
    )
    def test_coin_indexes(self):
        ov_pycoingecko_view.indexes([])

    @check_print(assert_in="═════════")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coingecko/test_coin_derivatives.yaml",
        record_mode="new_episodes",
    )
    def test_coin_derivatives(self):
        ov_pycoingecko_view.derivatives([])

    @check_print(assert_in="Index")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coingecko/test_coin_exchange_rates.yaml",
        record_mode="new_episodes",
    )
    def test_coin_exchange_rates(self):
        ov_pycoingecko_view.exchange_rates([])

    @check_print(assert_in="Metric")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coingecko/test_coin_global_market_info.yaml",
        record_mode="new_episodes",
    )
    def test_coin_global_market_info(self):
        ov_pycoingecko_view.global_market_info([])

    @check_print(assert_in="Metric")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coingecko/test_coin_global_defo_info.yaml",
        record_mode="new_episodes",
    )
    def test_coin_global_defi_info(self):
        ov_pycoingecko_view.global_defi_info([])

    # TODO: Re-add tests for coin_list and find
