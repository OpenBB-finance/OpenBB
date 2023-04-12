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


@pytest.mark.record_http
@pytest.mark.parametrize(
    "financial, quarterly, ratios, plot",
    [
        ("income", True, False, False),
        ("income", False, False, False),
        ("balance", False, False, False),
        ("cash", True, False, False),
        ("cash", False, False, False),
    ],
)
def test_display_fundamentals(financial, quarterly, ratios, plot):
    polygon_view.display_fundamentals(
        symbol="AAPL",
        statement=financial,
        limit=2,
        quarterly=quarterly,
        ratios=ratios,
        plot=plot,
        export="",
    )
