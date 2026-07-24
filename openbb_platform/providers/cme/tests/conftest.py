"""CME test configuration and cassette-based HTTP fixtures.

curl-cffi uses libcurl at the C level and cannot be intercepted by vcrpy.
Instead, record_http tests load pre-recorded JSON cassettes and patch
_get_json so tests are fully reproducible without network access.
"""

import json
from pathlib import Path

import pytest

CASSETTE_DIR = Path(__file__).parent / "cassettes"

_PRODUCTS = {
    "133": ("ES", "E-mini S&P 500 Futures", "CME", "Equities"),
    "146": ("NQ", "E-mini Nasdaq-100 Futures", "CME", "Equities"),
    "8667": ("MES", "Micro E-mini S&P 500 Futures", "CME", "Equities"),
    "8668": ("MNQ", "Micro E-mini Nasdaq-100 Futures", "CME", "Equities"),
    "318": ("YM", "E-mini Dow Futures", "CBOT", "Equities"),
}


def _load_cassette(symbol: str) -> dict:
    path = CASSETTE_DIR / f"{symbol.lower()}_settlements.json"
    return json.loads(path.read_text())


def _make_response(symbol: str) -> dict:
    cassette = _load_cassette(symbol)
    return {"settlements": cassette["settlements"]}


@pytest.fixture(autouse=True)
def cme_cassettes(request, monkeypatch, tmp_path):
    """Isolate catalog caches and replay HTTP cassettes for marked tests."""
    from openbb_cme.utils.catalog import clear_catalog_cache

    monkeypatch.setattr(
        "openbb_cme.utils.catalog._catalog_cache_path",
        lambda product_type: tmp_path / f"product_catalog_{product_type.lower()}.json",
    )
    clear_catalog_cache()
    request.addfinalizer(clear_catalog_cache)

    if not request.node.get_closest_marker("record_http"):
        return

    async def _patched_get_json(url: str, _client=None) -> dict:
        if "/services/product-slate" in url:
            products = [
                {
                    "id": int(pid),
                    "guid": f"TEST-{symbol}",
                    "prodCode": symbol,
                    "prodGroup": symbol,
                    "name": name,
                    "clearing": symbol,
                    "globex": symbol,
                    "floor": "-",
                    "floorTraded": False,
                    "globexTraded": True,
                    "cpc": symbol,
                    "venues": "Globex ClearPort",
                    "cleared": "Futures",
                    "exch": exchange,
                    "url": f"/markets/test/{symbol.lower()}_contract_specifications.html",
                    "cat": "-",
                    "subCat": "-",
                    "group": asset_class,
                    "subGroup": "Index",
                    "vol": "1,000",
                    "oi": "2,000",
                }
                for pid, (symbol, name, exchange, asset_class) in _PRODUCTS.items()
            ]
            return {
                "products": products,
                "props": {"pageTotal": 1, "pageNumber": 1},
            }

        for pid, (sym, _name, _exchange, _asset_class) in _PRODUCTS.items():
            if f"/ContractSpecs/List/productId/{pid}" in url:
                multiplier = (
                    "5"
                    if sym in {"MES", "YM"}
                    else "2"
                    if sym == "MNQ"
                    else "20"
                    if sym == "NQ"
                    else "50"
                )
                return {
                    "ProductID": int(pid),
                    "ProductName": _name,
                    "ContractUnit": f"${multiplier} x Index",
                    "PriceQuotation": "U.S. dollars per index point",
                    "MinimumPriceFluctuation": {
                        "ticks": [{"type": "Outright", "mintk": "0.25 index points"}]
                    },
                    "ProductCode": {"CmeGlobex": sym},
                    "ListedContracts": {"contractMonthsList": []},
                    "TradingHours": {"vandhr": []},
                    "SettlementMethod": "Financially Settled",
                }
            if f"/ProductCalendar/Future/{pid}" in url:
                return [
                    {
                        "contractMonth": "Sep 2026",
                        "productCode": f"{sym}U26",
                        "firstTrade": "01 Sep 2024",
                        "lastTrade": "18 Sep 2026",
                        "settlement": "18 Sep 2026",
                    },
                    {
                        "contractMonth": "Dec 2026",
                        "productCode": f"{sym}Z26",
                        "firstTrade": "01 Dec 2024",
                        "lastTrade": "18 Dec 2026",
                        "settlement": "18 Dec 2026",
                    },
                ]
            if f"/{pid}/" in url:
                return _make_response(sym)
        return {"settlements": []}

    monkeypatch.setattr(
        "openbb_cme.utils.helpers._get_json",
        _patched_get_json,
    )
