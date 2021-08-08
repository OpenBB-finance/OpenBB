from unittest import TestCase, mock
import sys
import io

from gamestonk_terminal.cryptocurrency.due_diligence.coinpaprika_view import (
    exchanges,
    chart,
    load,
    events,
    twitter,
    markets,
    price_supply,
    basic,
    ta,
)
from gamestonk_terminal.cryptocurrency.discovery.coinpaprika_view import (
    search,
    coins,
    find,
)
from gamestonk_terminal.cryptocurrency.overview.coinpaprika_view import (
    global_market,
    exchange_markets,
    all_exchanges,
    all_platforms,
    all_coins_market_info,
    all_coins_info,
    contracts,
)


class TestCoinPaprikaView(TestCase):
    def test_global_markets(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        global_market([])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("market_cap_usd", capt)

    def test_coins(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        coins([])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("rank", capt)

    def test_all_coins_market_info(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        all_coins_market_info([])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("Displaying data vs USD", capt)

    def test_all_coins_info(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        all_coins_info([])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("Displaying data vs USD", capt)

    def test_all_exchanges(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        all_exchanges([])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("Displaying data vs USD", capt)

    def test_search(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        search(["-q", "bt"])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("category", capt)

    def test_all_platforms(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        all_platforms([])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("platform_id", capt)

    def test_contracts(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        contracts([])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("active", capt)

    def test_find(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        find(["-c", "BTC"])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("index", capt)

    def test_twitter(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        twitter("eth-ethereum", [])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("Couldn't find", capt)

    def test_events(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        events("eth-ethereum", [])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("description", capt)

    def test_exchanges(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        exchanges("btc-bitcoin", [])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("name", capt)

    def test_markets(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        markets("eth-ethereum", [])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("exchange", capt)

    @mock.patch("matplotlib.pyplot.show")
    def test_chart(self, mock_matplot):
        # pylint: disable=unused-argument
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        chart("btc-bitcoin", [])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("\n", capt)

    def test_exchange_markets(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        exchange_markets([])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("base_currency_name", capt)

    def price_supply(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        price_supply("btc", [])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("asset_platform_id", capt)

    def test_load(self):
        value = load(["-c", "BTC"])
        self.assertEqual(value, "btc-bitcoin")

    def test_ta(self):
        value = ta("eth-ethereum", [])
        print(value[0])
        self.assertIn("Open", value[0])

    def test_basic(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        basic("BTC", [])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("Metric", capt)
