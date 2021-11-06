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
from gamestonk_terminal.cryptocurrency.cryptocurrency_helpers import (
    plot_chart,
    load,
    load_ta_data,
)
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
    coin, _, _ = load(coin="bitcoin", source="cg")
    return coin


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
        mock_return, vs = load_ta_data(
            coin=self.coin,
            source="cg",
            currency="usd",
            days=30,
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
        plot_chart(coin=self.coin, source="cg", currency="usd", days=30)

    @check_print(assert_in="Market Cap Rank")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coingecko/test_coin_info.yaml",
        record_mode="new_episodes",
    )
    def test_coin_info(self):
        dd_pycoingecko_view.display_info(self.coin, export="")

    @check_print(assert_in="Homepage")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coingecko/test_coin_web.yaml",
        record_mode="new_episodes",
    )
    def test_coin_web(self):
        dd_pycoingecko_view.display_web(self.coin, export="")

    @check_print(assert_in="Metric")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coingecko/test_coin_social.yaml",
        record_mode="new_episodes",
    )
    def test_coin_social(self):
        dd_pycoingecko_view.display_social(self.coin, export="")

    @check_print(assert_in="Metric")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coingecko/test_coin_dev.yaml",
        record_mode="new_episodes",
    )
    def test_coin_dev(self):
        dd_pycoingecko_view.display_dev(self.coin, export="")

    @check_print(assert_in="Metric")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coingecko/test_coin_ath.yaml",
        record_mode="new_episodes",
    )
    def test_coin_ath(self):
        dd_pycoingecko_view.display_ath(self.coin, export="", currency="usd")

    @check_print(assert_in="Metric")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coingecko/test_coin_atl.yaml",
        record_mode="new_episodes",
    )
    def test_coin_atl(self):
        dd_pycoingecko_view.display_atl(self.coin, export="", currency="usd")

    @check_print(assert_in="Metric")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coingecko/test_coin_score.yaml",
        record_mode="new_episodes",
    )
    def test_coin_score(self):
        dd_pycoingecko_view.display_score(self.coin, export="")

    @check_print(assert_in="Metric")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coingecko/test_coin_bc.yaml",
        record_mode="new_episodes",
    )
    def test_coin_bc(self):
        dd_pycoingecko_view.display_bc(self.coin, export="")

    @check_print(assert_in="Metric")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coingecko/test_coin_market.yaml",
        record_mode="new_episodes",
    )
    def test_coin_market(self):
        dd_pycoingecko_view.display_market(self.coin, export="")

    @check_print(assert_in="Total Bitcoin Holdings")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coingecko/test_coin_overview.yaml",
        record_mode="new_episodes",
    )
    def test_coin_holdings_overview(self):
        ov_pycoingecko_view.display_holdings_overview(coin="bitcoin", export="")

    @check_print(assert_in="═══════")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coingecko/test_coin_holding_companies.yaml",
        record_mode="new_episodes",
    )
    def test_coin_holdings_companies_list(self):
        ov_pycoingecko_view.display_holdings_companies_list(
            coin="ethereum", export="", links=False
        )

    @check_print(assert_in="Rank")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coingecko/test_coin_gainers.yaml",
        record_mode="new_episodes",
    )
    def test_coin_gainers(self):
        disc_pycoingecko_view.display_gainers(
            period="24h", top=15, sortby="Change", descend=True, links=False, export=""
        )

    @check_print(assert_in="Rank")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coingecko/test_coin_losers.yaml",
        record_mode="new_episodes",
    )
    def test_coin_losers(self):
        disc_pycoingecko_view.display_losers(
            period="24h", top=15, sortby="Change", descend=True, links=False, export=""
        )

    @check_print(assert_in="CryptoBlades")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coingecko/test_coin_discover.yaml",
        record_mode="new_episodes",
    )
    def test_coin_discover(self):
        disc_pycoingecko_view.display_discover(
            category="trending",
            top=15,
            sortby="Rank",
            descend=True,
            links=False,
            export="",
        )

    @check_print(assert_in="═════════════")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coingecko/test_coin_news.yaml",
        record_mode="new_episodes",
    )
    def test_coin_news(self):
        ov_pycoingecko_view.display_news(
            top=15, sortby="Index", descend=True, links=False, export=""
        )

    @check_print(assert_in="Decentralized Finance")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coingecko/test_coin_categories.yaml",
        record_mode="new_episodes",
    )
    def test_coin_categories(self):
        ov_pycoingecko_view.display_categories(
            top=15, sortby="Rank", descend=True, links=False, export=""
        )

    @check_print(assert_in="════════")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coingecko/test_coin_recently_added.yaml",
        record_mode="new_episodes",
    )
    def test_coin_recently_added(self):
        disc_pycoingecko_view.display_recently_added(
            top=15, sortby="Rank", descend=True, links=False, export=""
        )

    @check_print(assert_in="════")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coingecko/test_coin_stablecoins.yaml",
        record_mode="new_episodes",
    )
    def test_coin_stablecoins(self):
        ov_pycoingecko_view.display_stablecoins(
            top=15, sortby="Rank", descend=True, links=False, export=""
        )

    @check_print(assert_in="════════")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coingecko/test_coin_yfarms.yaml",
        record_mode="new_episodes",
    )
    def test_coin_yfarms(self):
        disc_pycoingecko_view.display_yieldfarms(
            top=15, sortby="Rank", descend=True, export=""
        )

    @check_print(assert_in="════════")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coingecko/test_coin_top_volume_coins.yaml",
        record_mode="new_episodes",
    )
    def test_coin_top_volume_coins(self):
        disc_pycoingecko_view.display_top_volume_coins(
            top=15, sortby="Rank", descend=True, export=""
        )

    @check_print(assert_in="═════════")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coingecko/test_coin_top_defi_coins.yaml",
        record_mode="new_episodes",
    )
    def test_coin_top_defi_coins(self):
        disc_pycoingecko_view.display_top_defi_coins(
            top=15, sortby="Rank", descend=True, links=False, export=""
        )

    @check_print(assert_in="════════")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coingecko/test_coin_top_dex.yaml",
        record_mode="new_episodes",
    )
    def test_coin_top_dex(self):
        disc_pycoingecko_view.display_top_dex(
            top=15, sortby="Rank", descend=True, export=""
        )

    @check_print(assert_in="Metric")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coingecko/test_coin_nft_market-status.yaml",
        record_mode="new_episodes",
    )
    def test_coin_nft_market_status(self):
        ov_pycoingecko_view.display_nft_market_status(export="")

    @check_print(assert_in="═══════════")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coingecko/test_coin_exchanges.yaml",
        record_mode="new_episodes",
    )
    def test_coin_exchanges(self):
        ov_pycoingecko_view.display_exchanges(
            top=15, sortby="Rank", descend=True, links=False, export=""
        )

    @check_print(assert_in="Rank")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coingecko/test_coin_platforms.yaml",
        record_mode="new_episodes",
    )
    def test_coin_platforms(self):
        ov_pycoingecko_view.display_platforms(
            top=15, sortby="Rank", descend=True, export=""
        )

    @check_print(assert_in="Rank")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coingecko/test_coin_products.yaml",
        record_mode="new_episodes",
    )
    def test_coin_products(self):
        ov_pycoingecko_view.display_products(
            top=15, sortby="Rank", descend=True, export=""
        )

    @check_print(assert_in="Rank")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coingecko/test_coin_indexes.yaml",
        record_mode="new_episodes",
    )
    def test_coin_indexes(self):
        ov_pycoingecko_view.display_indexes(
            top=15, sortby="Rank", descend=True, export=""
        )

    @check_print(assert_in="═════════")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coingecko/test_coin_derivatives.yaml",
        record_mode="new_episodes",
    )
    def test_coin_derivatives(self):
        ov_pycoingecko_view.display_derivatives(
            top=15, sortby="Rank", descend=True, export=""
        )

    @check_print(assert_in="Index")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coingecko/test_coin_exchange_rates.yaml",
        record_mode="new_episodes",
    )
    def test_coin_exchange_rates(self):
        ov_pycoingecko_view.display_exchange_rates(
            top=15, sortby="Index", descend=True, export=""
        )

    @check_print(assert_in="Metric")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coingecko/test_coin_global_market_info.yaml",
        record_mode="new_episodes",
    )
    def test_coin_global_market_info(self):
        ov_pycoingecko_view.display_global_market_info(export="")

    @check_print(assert_in="Metric")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coingecko/test_coin_global_defo_info.yaml",
        record_mode="new_episodes",
    )
    def test_coin_global_defi_info(self):
        ov_pycoingecko_view.display_global_defi_info(export="")

    # TODO: Re-add tests for coin_list and find
