from unittest import TestCase

import pytest
from gamestonk_terminal.cryptocurrency.discovery import (
    pycoingecko_view as disc_pycoingecko_view,
)

from tests.helpers.helpers import check_print

# pylint: disable=R0904


class TestCoinGeckoAPI(TestCase):
    @check_print(assert_in="Rank")
    @pytest.mark.vcr
    def test_coin_gainers(self):
        disc_pycoingecko_view.display_gainers(
            period="24h", top=15, sortby="Change", descend=True, links=False, export=""
        )

    @pytest.mark.skip
    @pytest.mark.vcr
    def test_coin_losers(self):
        disc_pycoingecko_view.display_losers(
            period="24h", top=15, sortby="Change", descend=True, links=False, export=""
        )

    @check_print(assert_in="Rank")
    @pytest.mark.vcr
    def test_coin_discover(self):
        disc_pycoingecko_view.display_discover(
            category="trending",
            top=15,
            sortby="Rank",
            descend=True,
            links=False,
            export="",
        )

    @check_print(assert_in="Rank")
    @pytest.mark.vcr
    def test_coin_recently_added(self):
        disc_pycoingecko_view.display_recently_added(
            top=15, sortby="Rank", descend=True, links=False, export=""
        )

    @check_print(assert_in="Rank")
    @pytest.mark.vcr
    def test_coin_yfarms(self):
        disc_pycoingecko_view.display_yieldfarms(
            top=15, sortby="Rank", descend=True, export=""
        )

    @check_print(assert_in="Rank")
    @pytest.mark.vcr
    def test_coin_top_volume_coins(self):
        disc_pycoingecko_view.display_top_volume_coins(
            top=15, sortby="Rank", descend=True, export=""
        )

    @check_print(assert_in="Rank")
    @pytest.mark.vcr
    def test_coin_top_defi_coins(self):
        disc_pycoingecko_view.display_top_defi_coins(
            top=15, sortby="Rank", descend=True, links=False, export=""
        )

    @check_print(assert_in="Rank")
    @pytest.mark.vcr
    def test_coin_top_dex(self):
        disc_pycoingecko_view.display_top_dex(
            top=15, sortby="Rank", descend=True, export=""
        )
