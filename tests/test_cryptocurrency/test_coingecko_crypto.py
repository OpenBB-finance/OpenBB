from unittest import mock, TestCase
import json
import sys
import io

from pycoingecko import CoinGeckoAPI
from gamestonk_terminal.cryptocurrency.coingecko.pycoingecko_view import (
    load,
    ta,
    chart,
    info,
    web,
    social,
    dev,
    ath,
    atl,
    score,
    bc,
    market,
    holdings_overview,
    holdings_companies_list,
    gainers,
    losers,
    discover,
    news,
    categories,
    recently_added,
    stablecoins,
    yfarms,
    top_volume_coins,
    top_defi_coins,
    top_dex,
    top_nft,
    nft_of_the_day,
    nft_market_status,
    exchanges,
    platforms,
    products,
    indexes,
    derivatives,
    exchange_rates,
    global_market_info,
    global_defi_info,
    coin_list,
    find,
)
from gamestonk_terminal.cryptocurrency.coingecko.pycoingecko_coin_model import Coin

# pylint: disable=unused-import


@mock.patch(
    "gamestonk_terminal.cryptocurrency.coingecko.pycoingecko_view.CoinGeckoAPI.get_coin_market_chart_by_id"
)
def get_bitcoin(mock_load):
    # pylint: disable=unused-argument
    with open("tests/data/btc_usd_test_data.json") as f:
        sample_return = json.load(f)
    mock_load.return_value = sample_return
    return load(["-c", "bitcoin"])


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
        "gamestonk_terminal.cryptocurrency.coingecko.pycoingecko_view.CoinGeckoAPI.get_coin_market_chart_by_id"
    )
    def test_coin_api_load_df_for_ta(self, mock_load):
        """
        Mock load function through get_coin_market_chart_by_id.
        Mock returns a dict saved as .json
        """

        with open("tests/data/btc_usd_test_data.json") as f:
            sample_return = json.load(f)

        mock_load.return_value = sample_return
        coin = load(["-c", "bitcoin"])
        mock_return, vs = ta(coin, ["--vs", "usd"])
        self.assertTrue(mock_return.shape == (722, 2))
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
        chart(self.coin, [])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertEqual("\n", capt)

    def test_coin_info(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        info(self.coin, [])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("asset_platform_id", capt)

    def test_coin_web(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        web(self.coin, [])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("homepage", capt)

    def test_coin_social(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        social(self.coin, [])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("telegram", capt)

    def test_coin_dev(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        dev(self.coin, [])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("forks", capt)

    def test_coin_ath(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        ath(self.coin, [])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("ath_date_btc", capt)

    def test_coin_atl(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        atl(self.coin, [])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("atl_date_btc", capt)

    def test_coin_score(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        score(self.coin, [])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("twitter_followers", capt)

    def test_coin_bc(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        bc(self.coin, [])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("Metric", capt)

    def test_coin_market(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        market(self.coin, [])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("max_supply", capt)

    def test_coin_holdings_overview(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        holdings_overview([])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("Total Bitcoin Holdings", capt)

    def test_coin_holdings_companies_list(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        holdings_companies_list([])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("country", capt)

    def test_coin_gainers(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        gainers([])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("rank", capt)

    def test_coin_losers(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        losers([])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("rank", capt)

    def test_coin_discover(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        discover("trending", [])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("CryptoBlades", capt)

    def test_coin_news(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        news([])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("author", capt)

    def test_coin_categories(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        categories([])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("Decentralized Finance", capt)

    def test_coin_recently_added(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        recently_added([])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("rank", capt)

    def test_coin_stablecoins(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        stablecoins([])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("name", capt)

    def test_coin_yfarms(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        yfarms([])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("name", capt)

    def test_coin_top_volume_coins(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        top_volume_coins([])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("name", capt)

    def test_coin_top_defi_coins(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        top_defi_coins([])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("name", capt)

    def test_coin_top_dex(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        top_dex([])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("name", capt)

    def test_coin_top_nft(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        top_nft([])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("name", capt)

    def test_coin_nft_of_the_day(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        nft_of_the_day([])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("Metric", capt)

    def test_coin_nft_market_status(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        nft_market_status([])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("Metric", capt)

    def test_coin_exchanges(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        exchanges([])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("name", capt)

    def test_coin_platforms(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        platforms([])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("name", capt)

    def test_coin_products(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        products([])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("platform", capt)

    def test_coin_indexes(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        indexes([])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("name", capt)

    def test_coin_derivatives(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        derivatives([])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("price", capt)

    def test_coin_exchange_rates(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        exchange_rates([])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("name", capt)

    def test_coin_global_market_info(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        global_market_info([])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("Metric", capt)

    def test_coin_global_defi_info(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        global_defi_info([])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("name", capt)

    def test_coin_coin_list(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        coin_list([])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("name", capt)

    def test_coin_find(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        find(["-c", "bitcoin"])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("name", capt)
