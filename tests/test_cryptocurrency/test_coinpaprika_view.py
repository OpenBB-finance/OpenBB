from unittest import TestCase, mock
import sys
import io

import vcr

from gamestonk_terminal.cryptocurrency.coinpaprika import coinpaprika_view


class TestCoinPaprikaView(TestCase):
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coinpaprika/test_global_markets.yaml"
    )
    def test_global_markets(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        coinpaprika_view.global_market([])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("market_cap_usd", capt)

    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coinpaprika/test_coins.yaml"
    )
    def test_coins(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        coinpaprika_view.coins([])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("rank", capt)

    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coinpaprika/test_all_coins_info.yaml"
    )
    def test_all_coins_info(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        coinpaprika_view.all_coins_info([])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("Displaying data vs USD", capt)

    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coinpaprika/test_all_exchanges.yaml"
    )
    def test_all_exchanges(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        coinpaprika_view.all_exchanges([])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("Displaying data vs USD", capt)

    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coinpaprika/test_search.yaml"
    )
    def test_search(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        coinpaprika_view.search(["-q", "bt"])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("category", capt)

    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coinpaprika/test_all_platforms.yaml"
    )
    def test_all_platforms(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        coinpaprika_view.all_platforms([])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("platform_id", capt)

    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coinpaprika/test_contracts.yaml"
    )
    def test_contracts(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        coinpaprika_view.contracts([])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("active", capt)

    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coinpaprika/test_find.yaml"
    )
    def test_find(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        coinpaprika_view.find(["-c", "BTC"])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("index", capt)

    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coinpaprika/test_twitter.yaml"
    )
    def test_twitter(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        coinpaprika_view.twitter("eth-ethereum", [])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("Couldn't find", capt)

    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coinpaprika/test_events.yaml"
    )
    def test_events(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        coinpaprika_view.events("eth-ethereum", [])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("description", capt)

    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coinpaprika/test_exchanges.yaml"
    )
    def test_exchanges(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        coinpaprika_view.exchanges("btc-bitcoin", [])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("name", capt)

    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coinpaprika/test_markets.yaml"
    )
    def test_markets(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        coinpaprika_view.markets("eth-ethereum", [])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("exchange", capt)

    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coinpaprika/test_chart.yaml"
    )
    @mock.patch("matplotlib.pyplot.show")
    def test_chart(self, mock_matplot):
        # pylint: disable=unused-argument
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        coinpaprika_view.chart("btc-bitcoin", [])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("\n", capt)

    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coinpaprika/test_exchange_markets.yaml"
    )
    def test_exchange_markets(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        coinpaprika_view.exchange_markets([])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("base_currency_name", capt)

    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coinpaprika/test_price_supply.yaml"
    )
    def price_supply(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        coinpaprika_view.price_supply("btc", [])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("asset_platform_id", capt)

    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coinpaprika/test_load.yaml"
    )
    def test_load(self):
        value = coinpaprika_view.load(["-c", "BTC"])
        self.assertEqual(value, "btc-bitcoin")

    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coinpaprika/test_ta.yaml"
    )
    def test_ta(self):
        value = coinpaprika_view.ta("eth-ethereum", [])
        print(value[0])
        self.assertIn("Open", value[0])

    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coinpaprika/test_basic.yaml"
    )
    def test_basic(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        coinpaprika_view.basic("BTC", [])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("Metric", capt)
