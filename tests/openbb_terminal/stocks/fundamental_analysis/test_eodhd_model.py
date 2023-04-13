"""Test the EODHD model."""

import pandas as pd
import pytest

from openbb_terminal.stocks.fundamental_analysis import eodhd_model


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_query_parameters": [
            ("api_token", "MOCK_API_KEY"),
        ],
    }


@pytest.mark.record_http
@pytest.mark.parametrize(
    "symbol, statement, ratios",
    [
        ("TSLA", "balance", True),
        ("TSLA", "income", False),
        ("TSLA", "cash", False),
    ],
)
def test_get_financials(symbol, statement, ratios):
    """Test get_financials."""
    eodhd_model.get_financials(symbol=symbol, statement=statement, ratios=ratios)


@pytest.mark.parametrize(
    "symbol, statement, ratios",
    [
        ("TSLA", "balance", True),
        ("TSLA", "income", False),
        ("TSLA", "cash", False),
    ],
)
def test_get_financials_mocked(symbol, statement, ratios, mocker):
    mocker.patch(
        "openbb_terminal.stocks.fundamental_analysis.eodhd_model" + ".get_financials",
        return_value=pd.DataFrame(
            data=[
                ["2021-01-01", 0.1, 1000],
                ["2021-01-01", 0.12, 1200],
                ["2021-01-01", 0.14, 1400],
            ],
        ),
    )
    getattr(eodhd_model, "get_financials")(
        symbol=symbol, statement=statement, ratios=ratios
    )
