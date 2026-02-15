"""FRED client tests."""

from __future__ import annotations

import io
import json
from urllib.error import HTTPError

import pytest

from openbb_quant_ml.service import macro_fred_client as mfc


def test_fred_client_requires_api_key(monkeypatch):
    monkeypatch.delenv("FRED_API_KEY", raising=False)
    client = mfc.FredClient()
    with pytest.raises(mfc.FredApiKeyMissingError):
        client.search_series("unemployment")


def test_fred_client_retry_then_success(monkeypatch):
    monkeypatch.setenv("FRED_API_KEY", "dummy")
    client = mfc.FredClient()
    monkeypatch.setattr(mfc.time, "sleep", lambda *_args, **_kwargs: None)

    calls = {"n": 0}

    class _Resp:
        def __init__(self, payload: dict):
            self._payload = payload

        def read(self):
            return json.dumps(self._payload).encode("utf-8")

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    def fake_urlopen(*_args, **_kwargs):
        calls["n"] += 1
        if calls["n"] == 1:
            raise HTTPError("http://example.com", 429, "rate limit", hdrs=None, fp=io.BytesIO(b""))
        return _Resp({"seriess": [{"id": "UNRATE", "title": "Unemployment Rate"}]})

    monkeypatch.setattr(mfc, "urlopen", fake_urlopen)
    out = client.search_series("unemployment")
    assert calls["n"] >= 2
    assert out[0]["series_id"] == "UNRATE"
