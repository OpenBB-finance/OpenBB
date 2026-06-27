"""CME test configuration and cassette-based HTTP fixtures.

curl-cffi uses libcurl at the C level and cannot be intercepted by vcrpy.
Instead, record_http tests load pre-recorded JSON cassettes and patch
_get_json so tests are fully reproducible without network access.
"""

import json
from pathlib import Path
from unittest.mock import AsyncMock

import pytest

CASSETTE_DIR = Path(__file__).parent / "cassettes"


def _load_cassette(symbol: str) -> dict:
    path = CASSETTE_DIR / f"{symbol.lower()}_settlements.json"
    return json.loads(path.read_text())


def _make_response(symbol: str) -> dict:
    cassette = _load_cassette(symbol)
    return {"settlements": cassette["settlements"]}


@pytest.fixture(autouse=True)
def cme_cassettes(request, monkeypatch):
    """Replay cassettes for record_http tests; no-op for all others."""
    if not request.node.get_closest_marker("record_http"):
        return

    async def _patched_get_json(url: str) -> dict:
        # Derive symbol from the product-ID in the URL
        from openbb_cme.utils.helpers import CME_PRODUCT_MAP

        pid_to_sym = {v["product_id"]: k for k, v in CME_PRODUCT_MAP.items()}
        for pid, sym in pid_to_sym.items():
            if f"/{pid}/" in url:
                return _make_response(sym)
        return {"settlements": []}

    monkeypatch.setattr(
        "openbb_cme.utils.helpers._get_json",
        _patched_get_json,
    )
