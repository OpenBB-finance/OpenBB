from unittest import mock, TestCase
import json
import sys
import io
import os
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

    def test_get_coins(self):
        """Test that pycoingecko retrieves the major coins"""
        coins = CoinGeckoAPI().get_coins()
        bitcoin_list = [coin["id"] for coin in coins]
        test_coins = ["bitcoin", "ethereum", "dogecoin"]
        for test in test_coins:
            self.assertIn(test, bitcoin_list)

    @mock.patch("matplotlib.pyplot.show")
    def test_coin_chart(self, mock_matplot):
        # pylint: disable=unused-argument
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        dd_pycoingecko_view.chart(self.coin, [])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertEqual("\n", capt)

    def test_coin_info(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        dd_pycoingecko_view.info(self.coin, [])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("Market Cap Rank", capt)

    def test_coin_web(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        dd_pycoingecko_view.web(self.coin, [])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("Homepage", capt)

    def test_coin_social(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        dd_pycoingecko_view.social(self.coin, [])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("Telegram", capt)

    def test_coin_dev(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        dd_pycoingecko_view.dev(self.coin, [])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("Forks", capt)

    def test_coin_ath(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        dd_pycoingecko_view.ath(self.coin, [])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("All Time High USD", capt)

    def test_coin_atl(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        dd_pycoingecko_view.atl(self.coin, [])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("All Time Low USD", capt)

    def test_coin_score(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        dd_pycoingecko_view.score(self.coin, [])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("Twitter Followers", capt)

    def test_coin_bc(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        dd_pycoingecko_view.bc(self.coin, [])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("Metric", capt)

    def test_coin_market(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        dd_pycoingecko_view.market(self.coin, [])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("Max Supply", capt)

    def test_coin_holdings_overview(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        ov_pycoingecko_view.holdings_overview([])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("Total Bitcoin Holdings", capt)

    def test_coin_holdings_companies_list(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        ov_pycoingecko_view.holdings_companies_list([])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("Country", capt)

    def test_coin_gainers(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        disc_pycoingecko_view.gainers([])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("Rank", capt)

    def test_coin_losers(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        disc_pycoingecko_view.losers([])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("Rank", capt)

    def test_coin_discover(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        disc_pycoingecko_view.discover("trending", [])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("Rank", capt)

    def test_coin_news(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        ov_pycoingecko_view.news([])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("Author", capt)

    def test_coin_categories(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        ov_pycoingecko_view.categories([])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("Decentralized Finance", capt)

    def test_coin_recently_added(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        disc_pycoingecko_view.recently_added([])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("Rank", capt)

    def test_coin_stablecoins(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        ov_pycoingecko_view.stablecoins([])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("Name", capt)

    def test_coin_yfarms(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        disc_pycoingecko_view.yfarms([])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("Name", capt)

    def test_coin_top_volume_coins(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        disc_pycoingecko_view.top_volume_coins([])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("Name", capt)

    def test_coin_top_defi_coins(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        disc_pycoingecko_view.top_defi_coins([])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("Name", capt)

    def test_coin_top_dex(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        disc_pycoingecko_view.top_dex([])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("Name", capt)

    def test_coin_top_nft(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        disc_pycoingecko_view.top_nft([])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("Name", capt)

    # TODO: Fix this test
    # def test_coin_nft_of_the_day(self):
    #    capturedOutput = io.StringIO()
    #    sys.stdout = capturedOutput
    #    nft_of_the_day([])
    #    sys.stdout = sys.__stdout__
    #    capt = capturedOutput.getvalue()
    #    self.assertIn("Metric", capt)

    def test_coin_nft_market_status(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        ov_pycoingecko_view.nft_market_status([])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("Metric", capt)

    def test_coin_exchanges(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        ov_pycoingecko_view.exchanges([])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("Name", capt)

    def test_coin_platforms(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        ov_pycoingecko_view.platforms([])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("Name", capt)

    def test_coin_products(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        ov_pycoingecko_view.products([])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("Platform", capt)

    def test_coin_indexes(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        ov_pycoingecko_view.indexes([])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("Name", capt)

    def test_coin_derivatives(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        ov_pycoingecko_view.derivatives([])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("Price", capt)

    def test_coin_exchange_rates(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        ov_pycoingecko_view.exchange_rates([])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("Name", capt)

    def test_coin_global_market_info(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        ov_pycoingecko_view.global_market_info([])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("Metric", capt)

    def test_coin_global_defi_info(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        ov_pycoingecko_view.global_defi_info([])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("Name", capt)

    # TODO: Re-add tests for coin_list and find
