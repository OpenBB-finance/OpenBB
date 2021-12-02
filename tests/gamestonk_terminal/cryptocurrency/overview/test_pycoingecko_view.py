from unittest import TestCase

import vcr
from gamestonk_terminal.cryptocurrency.overview import (
    pycoingecko_view as ov_pycoingecko_view,
)

from tests.helpers import check_print

# pylint: disable=unused-import


# pylint: disable=R0904
class TestCoinGeckoAPI(TestCase):
    @check_print(assert_in="Total Bitcoin Holdings")
    @vcr.use_cassette(
        "tests/gamestonk_terminal/cryptocurrency/overview/cassettes/test_pycoingecko_view/test_coin_overview.yaml",
        record_mode="new_episodes",
    )
    def test_coin_holdings_overview(self):
        ov_pycoingecko_view.display_holdings_overview(coin="bitcoin", export="")

    @check_print(assert_in="═══════")
    @vcr.use_cassette(
        "tests/gamestonk_terminal/cryptocurrency/overview/cassettes/test_pycoingecko_view/test_coin_holding_companies.yaml",
        record_mode="new_episodes",
    )
    def test_coin_holdings_companies_list(self):
        ov_pycoingecko_view.display_holdings_companies_list(
            coin="ethereum", export="", links=False
        )

    @check_print(assert_in="═════════════")
    @vcr.use_cassette(
        "tests/gamestonk_terminal/cryptocurrency/overview/cassettes/test_pycoingecko_view/test_coin_news.yaml",
        record_mode="new_episodes",
    )
    def test_coin_news(self):
        ov_pycoingecko_view.display_news(
            top=15, sortby="Index", descend=True, links=False, export=""
        )

    @check_print(assert_in="Decentralized Finance")
    @vcr.use_cassette(
        "tests/gamestonk_terminal/cryptocurrency/overview/cassettes/test_pycoingecko_view/test_coin_categories.yaml",
        record_mode="new_episodes",
    )
    def test_coin_categories(self):
        ov_pycoingecko_view.display_categories(
            top=15, sortby="Rank", descend=True, links=False, export=""
        )

    @check_print(assert_in="════")
    @vcr.use_cassette(
        "tests/gamestonk_terminal/cryptocurrency/overview/cassettes/test_pycoingecko_view/test_coin_stablecoins.yaml",
        record_mode="new_episodes",
    )
    def test_coin_stablecoins(self):
        ov_pycoingecko_view.display_stablecoins(
            top=15, sortby="Rank", descend=True, links=False, export=""
        )

    @check_print(assert_in="Metric")
    @vcr.use_cassette(
        "tests/gamestonk_terminal/cryptocurrency/overview/cassettes/test_pycoingecko_view/test_coin_nft_market-status.yaml",
        record_mode="new_episodes",
    )
    def test_coin_nft_market_status(self):
        ov_pycoingecko_view.display_nft_market_status(export="")

    @check_print(assert_in="═══════════")
    @vcr.use_cassette(
        "tests/gamestonk_terminal/cryptocurrency/overview/cassettes/test_pycoingecko_view/test_coin_exchanges.yaml",
        record_mode="new_episodes",
    )
    def test_coin_exchanges(self):
        ov_pycoingecko_view.display_exchanges(
            top=15, sortby="Rank", descend=True, links=False, export=""
        )

    @check_print(assert_in="Rank")
    @vcr.use_cassette(
        "tests/gamestonk_terminal/cryptocurrency/overview/cassettes/test_pycoingecko_view/test_coin_platforms.yaml",
        record_mode="new_episodes",
    )
    def test_coin_platforms(self):
        ov_pycoingecko_view.display_platforms(
            top=15, sortby="Rank", descend=True, export=""
        )

    @check_print(assert_in="Rank")
    @vcr.use_cassette(
        "tests/gamestonk_terminal/cryptocurrency/overview/cassettes/test_pycoingecko_view/test_coin_products.yaml",
        record_mode="new_episodes",
    )
    def test_coin_products(self):
        ov_pycoingecko_view.display_products(
            top=15, sortby="Rank", descend=True, export=""
        )

    @check_print(assert_in="Rank")
    @vcr.use_cassette(
        "tests/gamestonk_terminal/cryptocurrency/overview/cassettes/test_pycoingecko_view/test_coin_indexes.yaml",
        record_mode="new_episodes",
    )
    def test_coin_indexes(self):
        ov_pycoingecko_view.display_indexes(
            top=15, sortby="Rank", descend=True, export=""
        )

    @check_print(assert_in="═════════")
    @vcr.use_cassette(
        "tests/gamestonk_terminal/cryptocurrency/overview/cassettes/test_pycoingecko_view/test_coin_derivatives.yaml",
        record_mode="new_episodes",
    )
    def test_coin_derivatives(self):
        ov_pycoingecko_view.display_derivatives(
            top=15, sortby="Rank", descend=True, export=""
        )

    @check_print(assert_in="Index")
    @vcr.use_cassette(
        "tests/gamestonk_terminal/cryptocurrency/overview/cassettes/test_pycoingecko_view/test_coin_exchange_rates.yaml",
        record_mode="new_episodes",
    )
    def test_coin_exchange_rates(self):
        ov_pycoingecko_view.display_exchange_rates(
            top=15, sortby="Index", descend=True, export=""
        )

    @check_print(assert_in="Metric")
    @vcr.use_cassette(
        "tests/gamestonk_terminal/cryptocurrency/overview/cassettes/test_pycoingecko_view/test_coin_global_market_info.yaml",
        record_mode="new_episodes",
    )
    def test_coin_global_market_info(self):
        ov_pycoingecko_view.display_global_market_info(export="")

    @check_print(assert_in="Metric")
    @vcr.use_cassette(
        "tests/gamestonk_terminal/cryptocurrency/overview/cassettes/test_pycoingecko_view/test_coin_global_defo_info.yaml",
        record_mode="new_episodes",
    )
    def test_coin_global_defi_info(self):
        ov_pycoingecko_view.display_global_defi_info(export="")
