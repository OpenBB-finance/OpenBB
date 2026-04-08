import pytest
from openbb_headless_oracle.models.market_state import HeadlessOracleMarketStateFetcher


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [None],
    }


@pytest.mark.record_http
def test_headless_oracle_market_state_fetcher():
    params = {"exchange": "XNYS"}

    fetcher = HeadlessOracleMarketStateFetcher()
    result = fetcher.test(params, None)
    assert result is None
