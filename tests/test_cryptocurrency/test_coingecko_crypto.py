from unittest import mock, TestCase
import json

import vcr

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
)
from gamestonk_terminal.cryptocurrency.coingecko.pycoingecko_coin_model import Coin
from tests.helpers import check_print


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

    @check_print()
    def test_coin_api_load(self):
        """
        Mock load function through get_coin_market_chart_by_id.
        Mock returns a dict saved as .json

        """
        self.assertEqual(self.coin.coin_symbol, "bitcoin")
        self.assertIsInstance(self.coin, Coin)

    @check_print()
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

    @check_print()
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coingecko/test_get_coins.yaml"
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
        chart(self.coin, [])

    @check_print(assert_in="asset_platform_id")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coingecko/test_coin_info.yaml"
    )
    def test_coin_info(self):
        info(self.coin, [])

    @check_print(assert_in="homepage")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coingecko/test_coin_web.yaml"
    )
    def test_coin_web(self):
        web(self.coin, [])

    @check_print(assert_in="telegram")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coingecko/test_coin_social.yaml"
    )
    def test_coin_social(self):
        social(self.coin, [])

    @check_print(assert_in="forks")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coingecko/test_coin_dev.yaml"
    )
    def test_coin_dev(self):
        dev(self.coin, [])

    @check_print(assert_in="ath_date_btc")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coingecko/test_coin_ath.yaml"
    )
    def test_coin_ath(self):
        ath(self.coin, [])

    @check_print(assert_in="atl_date_btc")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coingecko/test_coin_atl.yaml"
    )
    def test_coin_atl(self):
        atl(self.coin, [])

    @check_print(assert_in="twitter_followers")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coingecko/test_coin_score.yaml"
    )
    def test_coin_score(self):
        score(self.coin, [])

    @check_print(assert_in="Metric")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coingecko/test_coin_bc.yaml"
    )
    def test_coin_bc(self):
        bc(self.coin, [])

    @check_print(assert_in="max_supply")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coingecko/test_coin_market.yaml"
    )
    def test_coin_market(self):
        market(self.coin, [])

    @check_print(assert_in="Total Bitcoin Holdings")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coingecko/test_coin_overview.yaml"
    )
    def test_coin_holdings_overview(self):
        holdings_overview([])

    @check_print(assert_in="country")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coingecko/test_coin_holding_comapnies.yaml"
    )
    def test_coin_holdings_companies_list(self):
        holdings_companies_list([])

    @check_print(assert_in="rank")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coingecko/test_coin_gainers.yaml"
    )
    def test_coin_gainers(self):
        gainers([])

    @check_print(assert_in="rank")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coingecko/test_coin_losers.yaml"
    )
    def test_coin_losers(self):
        losers([])

    @check_print(assert_in="CryptoBlades")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coingecko/test_coin_discover.yaml"
    )
    def test_coin_discover(self):
        discover("trending", [])

    @check_print(assert_in="author")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coingecko/test_coin_news.yaml"
    )
    def test_coin_news(self):
        news([])

    @check_print(assert_in="Decentralized Finance")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coingecko/test_coin_categories.yaml"
    )
    def test_coin_categories(self):
        categories([])

    @check_print(assert_in="rank")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coingecko/test_coin_recently_added.yaml"
    )
    def test_coin_recently_added(self):
        recently_added([])

    @check_print(assert_in="name")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coingecko/test_coin_stablecoins.yaml"
    )
    def test_coin_stablecoins(self):
        stablecoins([])

    @check_print(assert_in="name")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coingecko/test_coin_yfarms.yaml"
    )
    def test_coin_yfarms(self):
        yfarms([])

    @check_print(assert_in="name")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coingecko/test_coin_top_volume_coins.yaml"
    )
    def test_coin_top_volume_coins(self):
        top_volume_coins([])

    @check_print(assert_in="name")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coingecko/test_coin_top_defi_coins.yaml"
    )
    def test_coin_top_defi_coins(self):
        top_defi_coins([])

    @check_print(assert_in="name")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coingecko/test_coin_top_dex.yaml"
    )
    def test_coin_top_dex(self):
        top_dex([])

    @check_print(assert_in="name")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coingecko/test_coin_top_nft.yaml"
    )
    def test_coin_top_nft(self):
        top_nft([])

    @check_print(assert_in="Metric")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coingecko/test_coin_nft_of_day.yaml"
    )
    def test_coin_nft_of_the_day(self):
        nft_of_the_day([])

    @check_print(assert_in="Metric")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coingecko/test_coin_nft_market-status.yaml"
    )
    def test_coin_nft_market_status(self):
        nft_market_status([])

    @check_print(assert_in="name")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coingecko/test_coin_exchanges.yaml"
    )
    def test_coin_exchanges(self):
        exchanges([])

    @check_print(assert_in="name")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coingecko/test_coin_platforms.yaml"
    )
    def test_coin_platforms(self):
        platforms([])

    @check_print(assert_in="platform")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coingecko/test_coin_products.yaml"
    )
    def test_coin_products(self):
        products([])

    @check_print(assert_in="name")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coingecko/test_coin_indexes.yaml"
    )
    def test_coin_indexes(self):
        indexes([])

    @check_print(assert_in="price")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coingecko/test_coin_derivatives.yaml"
    )
    def test_coin_derivatives(self):
        derivatives([])

    @check_print(assert_in="name")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coingecko/test_coin_exchange_rates.yaml"
    )
    def test_coin_exchange_rates(self):
        exchange_rates([])

    @check_print(assert_in="Metric")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coingecko/test_coin_global_market_info.yaml"
    )
    def test_coin_global_market_info(self):
        global_market_info([])

    @check_print(assert_in="name")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coingecko/test_coin_global_defo_info.yaml"
    )
    def test_coin_global_defi_info(self):
        global_defi_info([])
