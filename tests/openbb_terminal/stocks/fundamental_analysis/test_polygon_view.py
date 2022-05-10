import pytest
from openbb_terminal.stocks.fundamental_analysis import polygon_view


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [
            ("apiKey", "MOCK_API_KEY"),
        ],
    }


@pytest.mark.record_stdout
@pytest.mark.vcr
@pytest.mark.parametrize(
    "financial, quarterly",
    [("income", True), ("income", False), ("balance", True), ("balance", False)],
)
def test_display_fundamentals(financial, quarterly):
    polygon_view.display_fundamentals(
        ticker="AAPL", financial=financial, limit=2, quarterly=quarterly, export=""
    )
