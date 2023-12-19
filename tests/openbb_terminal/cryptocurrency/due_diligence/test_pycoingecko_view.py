import json
from unittest import TestCase, mock

import pytest
import vcr

from openbb_terminal.cryptocurrency.cryptocurrency_helpers import load
from openbb_terminal.cryptocurrency.due_diligence import pycoingecko_view
from tests.helpers.helpers import check_print

# pylint: disable=unused-import

pytest.skip(msg="Pycoingecko tests have not been migrated.", allow_module_level=True)


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_display_potential_returns():
    pycoingecko_view.display_coin_potential_returns(
        to_symbol="algorand", from_symbol="bitcoin"
    )


@mock.patch(
    "openbb_terminal.cryptocurrency.due_diligence.pycoingecko_model.CoinGeckoAPI.get_coin_market_chart_by_id"
)
def get_bitcoin(mock_load):
    # pylint: disable=unused-argument
    with open(
        "tests/openbb_terminal/cryptocurrency/due_diligence/json/test_pycoingecko_view/btc_usd_test_data.json",
        encoding="utf8",
    ) as f:
        sample_return = json.load(f)
    mock_load.return_value = sample_return
    df = load("btc", to_symbol="usd", source="YahooFinance")
    return df


# pylint: disable=R0904
class TestCoinGeckoAPI(TestCase):
    # pylint: disable = no-value-for-parameter
    coin = "btc"

    @check_print(assert_in="Market Cap Rank")
    @vcr.use_cassette(
        "tests/openbb_terminal/cryptocurrency/due_diligence/cassettes/test_pycoingecko_view/test_coin_info.yaml",
        record_mode="none",
    )
    def test_coin_info(self):
        pycoingecko_view.display_info(self.coin, export="")

    @check_print(assert_in="Homepage")
    @vcr.use_cassette(
        "tests/openbb_terminal/cryptocurrency/due_diligence/cassettes/test_pycoingecko_view/test_coin_web.yaml",
        record_mode="none",
    )
    def test_coin_web(self):
        pycoingecko_view.display_web(self.coin, export="")

    @check_print(assert_in="Metric")
    @vcr.use_cassette(
        "tests/openbb_terminal/cryptocurrency/due_diligence/cassettes/test_pycoingecko_view/test_coin_social.yaml",
        record_mode="none",
    )
    def test_coin_social(self):
        pycoingecko_view.display_social(self.coin, export="")

    @check_print(assert_in="Metric")
    @vcr.use_cassette(
        "tests/openbb_terminal/cryptocurrency/due_diligence/cassettes/test_pycoingecko_view/test_coin_dev.yaml",
        record_mode="none",
    )
    def test_coin_dev(self):
        pycoingecko_view.display_dev(self.coin, export="")

    @check_print(assert_in="Metric")
    @vcr.use_cassette(
        "tests/openbb_terminal/cryptocurrency/due_diligence/cassettes/test_pycoingecko_view/test_coin_ath.yaml",
        record_mode="none",
    )
    def test_coin_ath(self):
        pycoingecko_view.display_ath(self.coin, export="", currency="usd")

    @check_print(assert_in="Metric")
    @vcr.use_cassette(
        "tests/openbb_terminal/cryptocurrency/due_diligence/cassettes/test_pycoingecko_view/test_coin_atl.yaml",
        record_mode="none",
    )
    def test_coin_atl(self):
        pycoingecko_view.display_atl(self.coin, export="", currency="usd")

    @check_print(assert_in="Metric")
    @vcr.use_cassette(
        "tests/openbb_terminal/cryptocurrency/due_diligence/cassettes/test_pycoingecko_view/test_coin_score.yaml",
        record_mode="none",
    )
    def test_coin_score(self):
        pycoingecko_view.display_score(self.coin, export="")

    @check_print(assert_in="Metric")
    @vcr.use_cassette(
        "tests/openbb_terminal/cryptocurrency/due_diligence/cassettes/test_pycoingecko_view/test_coin_bc.yaml",
        record_mode="none",
    )
    def test_coin_bc(self):
        pycoingecko_view.display_bc(self.coin, export="")

    @check_print(assert_in="Metric")
    @vcr.use_cassette(
        "tests/openbb_terminal/cryptocurrency/due_diligence/cassettes/test_pycoingecko_view/test_coin_market.yaml",
        record_mode="none",
    )
    def test_coin_market(self):
        pycoingecko_view.display_market(self.coin, export="")
