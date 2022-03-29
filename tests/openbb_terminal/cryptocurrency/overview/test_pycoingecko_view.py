from unittest import TestCase

import pytest
from openbb_terminal.cryptocurrency.overview import (
    pycoingecko_view as ov_pycoingecko_view,
)

# pylint: disable=unused-import


# pylint: disable=R0904
class TestCoinGeckoAPI(TestCase):
    @pytest.mark.skip
    @pytest.mark.record_stdout
    @pytest.mark.vcr()
    def test_coin_holdings_overview(self):
        ov_pycoingecko_view.display_holdings_overview(
            coin="bitcoin", show_bar=False, export="", top=20
        )

    @pytest.mark.record_stdout
    @pytest.mark.vcr()
    def test_coin_categories(self):
        ov_pycoingecko_view.display_categories(
            top=15, export="", pie=False, sortby="market_cap"
        )

    @pytest.mark.skip
    @pytest.mark.record_stdout
    @pytest.mark.vcr()
    def test_coin_stablecoins(self):
        ov_pycoingecko_view.display_stablecoins(
            top=15, export="", sortby="market_cap", pie=False, descend=False
        )

    @pytest.mark.record_stdout
    @pytest.mark.vcr()
    def test_coin_exchanges(self):
        ov_pycoingecko_view.display_exchanges(
            top=15, sortby="Rank", descend=True, links=False, export=""
        )

    @pytest.mark.record_stdout
    @pytest.mark.vcr()
    def test_coin_platforms(self):
        ov_pycoingecko_view.display_platforms(
            top=15, sortby="Rank", descend=True, export=""
        )

    @pytest.mark.record_stdout
    @pytest.mark.vcr()
    def test_coin_products(self):
        ov_pycoingecko_view.display_products(
            top=15, sortby="Rank", descend=True, export=""
        )

    @pytest.mark.record_stdout
    @pytest.mark.vcr()
    def test_coin_indexes(self):
        ov_pycoingecko_view.display_indexes(
            top=15, sortby="Rank", descend=True, export=""
        )

    @pytest.mark.record_stdout
    @pytest.mark.vcr()
    def test_coin_derivatives(self):
        ov_pycoingecko_view.display_derivatives(
            top=15, sortby="Rank", descend=True, export=""
        )

    @pytest.mark.record_stdout
    @pytest.mark.vcr()
    def test_coin_exchange_rates(self):
        ov_pycoingecko_view.display_exchange_rates(
            top=15, sortby="Index", descend=True, export=""
        )

    @pytest.mark.record_stdout
    @pytest.mark.vcr()
    def test_coin_global_market_info(self):
        ov_pycoingecko_view.display_global_market_info(export="", pie=False)

    @pytest.mark.record_stdout
    @pytest.mark.vcr()
    def test_coin_global_defi_info(self):
        ov_pycoingecko_view.display_global_defi_info(export="")
