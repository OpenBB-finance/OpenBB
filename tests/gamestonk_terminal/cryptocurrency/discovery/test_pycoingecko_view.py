from unittest import TestCase

import vcr
from gamestonk_terminal.cryptocurrency.discovery import (
    pycoingecko_view as disc_pycoingecko_view,
)

from tests.helpers import check_print

# pylint: disable=unused-import


# pylint: disable=R0904
class TestCoinGeckoAPI(TestCase):
    @check_print(assert_in="Rank")
    @vcr.use_cassette(
        "tests/gamestonk_terminal/cryptocurrency/discovery/cassettes/test_pycoingecko_view/gainers.yaml",
        record_mode="new_episodes",
    )
    def test_coin_gainers(self):
        disc_pycoingecko_view.display_gainers(
            period="24h", top=15, sortby="Change", descend=True, links=False, export=""
        )

    @check_print(assert_in="Rank")
    @vcr.use_cassette(
        "tests/gamestonk_terminal/cryptocurrency/discovery/cassettes/test_pycoingecko_view/losers.yaml",
        record_mode="new_episodes",
    )
    def test_coin_losers(self):
        disc_pycoingecko_view.display_losers(
            period="24h", top=15, sortby="Change", descend=True, links=False, export=""
        )

    @check_print(assert_in="CryptoBlades")
    @vcr.use_cassette(
        "tests/gamestonk_terminal/cryptocurrency/discovery/cassettes/test_pycoingecko_view/discover.yaml",
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

    @check_print(assert_in="════════")
    @vcr.use_cassette(
        "tests/gamestonk_terminal/cryptocurrency/discovery/cassettes/test_pycoingecko_view/recently_added.yaml",
        record_mode="new_episodes",
    )
    def test_coin_recently_added(self):
        disc_pycoingecko_view.display_recently_added(
            top=15, sortby="Rank", descend=True, links=False, export=""
        )

    @check_print(assert_in="════════")
    @vcr.use_cassette(
        "tests/gamestonk_terminal/cryptocurrency/discovery/cassettes/test_pycoingecko_view/yfarms.yaml",
        record_mode="new_episodes",
    )
    def test_coin_yfarms(self):
        disc_pycoingecko_view.display_yieldfarms(
            top=15, sortby="Rank", descend=True, export=""
        )

    @check_print(assert_in="════════")
    @vcr.use_cassette(
        "tests/gamestonk_terminal/cryptocurrency/discovery/cassettes/test_pycoingecko_view/top_volume_coins.yaml",
        record_mode="new_episodes",
    )
    def test_coin_top_volume_coins(self):
        disc_pycoingecko_view.display_top_volume_coins(
            top=15, sortby="Rank", descend=True, export=""
        )

    @check_print(assert_in="═════════")
    @vcr.use_cassette(
        "tests/gamestonk_terminal/cryptocurrency/discovery/cassettes/test_pycoingecko_view/top_defi_coins.yaml",
        record_mode="new_episodes",
    )
    def test_coin_top_defi_coins(self):
        disc_pycoingecko_view.display_top_defi_coins(
            top=15, sortby="Rank", descend=True, links=False, export=""
        )

    @check_print(assert_in="════════")
    @vcr.use_cassette(
        "tests/gamestonk_terminal/cryptocurrency/discovery/cassettes/test_pycoingecko_view/top_dex.yaml",
        record_mode="new_episodes",
    )
    def test_coin_top_dex(self):
        disc_pycoingecko_view.display_top_dex(
            top=15, sortby="Rank", descend=True, export=""
        )
