"""Shared fixtures for the openbb_government_us test suite."""

import pytest


def _redact_binary_response(response: dict) -> dict:
    headers = response.get("headers", {})
    content_type_values = (
        headers.get("Content-Type") or headers.get("content-type") or []
    )
    content_type = " ".join(content_type_values).lower()
    body = response.get("body", {})
    payload = body.get("string")
    if isinstance(payload, str):
        payload_bytes = payload.encode("utf-8", errors="ignore")
    else:
        payload_bytes = payload
    is_pdf = (
        "application/pdf" in content_type or "application/octet-stream" in content_type
    )
    if is_pdf and isinstance(payload_bytes, (bytes, bytearray)):
        body["string"] = b"%PDF-1.4\n%OpenBB VCR redacted binary body\n%%EOF\n"
        response["body"] = body
    return response


@pytest.fixture(scope="module")
def vcr_config():
    """VCR configuration: strip auth headers and api_key from recorded cassettes."""
    return {
        "filter_headers": [
            ("User-Agent", None),
            ("api_key", "MOCK_API_KEY"),
        ],
        "filter_query_parameters": [
            ("api_key", "MOCK_API_KEY"),
        ],
        "before_record_response": _redact_binary_response,
    }


@pytest.fixture(autouse=True)
def _clear_state_caches():
    """Reset module-level caches so state never leaks between tests."""
    from openbb_government_us.congress.utils import bulk, committees
    from openbb_government_us.congress.utils.helpers import BillsState

    def _reset():
        BillsState().bulk.clear()
        committees._GOVTRACK_DATA_CACHE.clear()
        bulk._LOAD_LOCKS.clear()

    _reset()
    yield
    _reset()


@pytest.fixture(autouse=True)
def _isolate_ers_cache(tmp_path, monkeypatch):
    """Point the ERS disk cache at a per-test directory so HTTP always fires."""
    monkeypatch.setenv("OPENBB_USDA_CACHE_DIR", str(tmp_path / "ers_cache"))
