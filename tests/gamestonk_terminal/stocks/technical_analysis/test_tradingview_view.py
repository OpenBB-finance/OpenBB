# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.stocks.technical_analysis import tradingview_view


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_query_parameters": [
            ("apikey", "MOCK_API_KEY"),
        ]
    }


@pytest.mark.vcr
# @pytest.mark.record_stdout
def test_print_recommendation():
    tradingview_view.print_recommendation(
        ticker="AAPL",
        exchange="",
        screener="america",
        interval="",
        export="",
    )
