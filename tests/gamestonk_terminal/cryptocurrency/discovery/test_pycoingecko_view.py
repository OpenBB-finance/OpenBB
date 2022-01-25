from unittest import TestCase

import vcr
import pytest
from gamestonk_terminal.cryptocurrency.discovery import (
    pycoingecko_view as disc_pycoingecko_view,
)

from tests.helpers.helpers import check_print

# pylint: disable=R0904


class TestCoinGeckoAPI(TestCase):
    @pytest.mark.skip
    @check_print(assert_in="Rank")
    @pytest.mark.vcr
    def test_coin_gainers(self):
        disc_pycoingecko_view.display_gainers(
            period="24h", top=15, export="", sortby=""
        )

    @pytest.mark.skip
    @check_print(assert_in="Rank")
    @vcr.use_cassette(
        "tests/gamestonk_terminal/cryptocurrency/discovery/cassettes/test_pycoingecko_view/losers.yaml",
        record_mode="new_episodes",
    )
    def test_coin_losers(self):
        disc_pycoingecko_view.display_losers(period="24h", top=15, export="", sortby="")
