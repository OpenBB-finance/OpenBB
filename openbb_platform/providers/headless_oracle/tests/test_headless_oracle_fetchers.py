from datetime import datetime, timezone

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


def test_headless_oracle_market_state_transform_data_fail_closed():
    query = HeadlessOracleMarketStateFetcher.transform_query({"exchange": "XNYS"})
    payload = {
        "receipt": {
            "mic": "XNYS",
            "status": "UNKNOWN",
            "issued_at": "2026-04-08T18:26:25.387Z",
            "expires_at": "2026-04-08T18:27:25.387Z",
            "issuer": "headlessoracle.com",
            "source": "SCHEDULE",
            "halt_detection": "active",
            "receipt_mode": "demo",
            "schema_version": "v5.0",
            "public_key_id": "key_2026_v1",
            "signature": "sig",
        }
    }

    result = HeadlessOracleMarketStateFetcher.transform_data(query, payload)

    assert result.exchange == "NYSE"
    assert result.mic == "XNYS"
    assert result.status == "UNKNOWN"
    assert result.is_open is False
    assert result.issued_at == datetime(2026, 4, 8, 18, 26, 25, 387000, tzinfo=timezone.utc)
    assert result.expires_at == datetime(2026, 4, 8, 18, 27, 25, 387000, tzinfo=timezone.utc)
    assert result.ttl_seconds == 60
    assert result.issuer == "headlessoracle.com"
    assert result.source == "SCHEDULE"
    assert result.halt_detection == "active"
    assert result.receipt_mode == "demo"
    assert result.schema_version == "v5.0"
    assert result.public_key_id == "key_2026_v1"
    assert result.signature == "sig"
