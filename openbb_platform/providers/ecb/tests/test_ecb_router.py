import asyncio
import json

from openbb_ecb import ecb_router as router_module
from openbb_ecb.utils.metadata import EcbMetadata

_META = EcbMetadata()


def test_list_and_search_dataflows():
    every = asyncio.run(router_module.list_dataflows(_META))
    assert any(d["value"] == "EXR" for d in every)
    assert any(
        d["value"] == "EXR"
        for d in asyncio.run(router_module.search_dataflows(_META, "exchange"))
    )
    assert len(asyncio.run(router_module.search_dataflows(_META, None))) == len(every)


def test_topics_commands():
    topics = asyncio.run(router_module.list_topics(_META))
    assert topics
    rows = asyncio.run(router_module.topic_dataflows(_META, topics[0]["value"]))
    assert rows
    assert all(isinstance(r, dict) and "value" in r for r in rows)


def test_get_dataflow_dimensions():
    dims = asyncio.run(router_module.get_dataflow_dimensions(_META, "EXR"))
    assert [d["id"] for d in dims][0] == "FREQ"


def test_dimension_choices_no_selections():
    out = asyncio.run(router_module.dimension_choices(_META, "EXR", "CURRENCY", None))
    assert out == _META.resolve_dimension_values("EXR", "CURRENCY")


def test_dimension_choices_narrowed(monkeypatch):
    monkeypatch.setattr(
        _META, "_fetch_available_constraint", lambda flow, key: {"CURRENCY": ["USD"]}
    )
    out = asyncio.run(
        router_module.dimension_choices(_META, "EXR", "CURRENCY", "FREQ=D,bare")
    )
    assert {o["value"] for o in out} == {"USD"}


def test_dimension_choices_no_availability(monkeypatch):
    monkeypatch.setattr(_META, "_fetch_available_constraint", lambda flow, key: {})
    out = asyncio.run(
        router_module.dimension_choices(_META, "EXR", "CURRENCY", "FREQ=D")
    )
    assert out == _META.resolve_dimension_values("EXR", "CURRENCY")


def test_model_commands(monkeypatch):

    class _FakeOBBject:
        @staticmethod
        async def from_query(query):
            return ("OBBJECT", query)

    monkeypatch.setattr(router_module, "OBBQuery", lambda **kwargs: kwargs)
    monkeypatch.setattr(router_module, "OBBject", _FakeOBBject)
    commands = [
        router_module.available_indicators,
        router_module.indicators,
        router_module.balance_of_payments,
        router_module.calendar,
        router_module.exchange_rates,
        router_module.reference_rates,
        router_module.yield_curve,
        router_module.key_interest_rates,
        router_module.euro_short_term_rate,
        router_module.mfi_interest_rates,
        router_module.eligible_assets,
    ]
    for command in commands:
        result = asyncio.run(command(None, None, None, None))
        assert result[0] == "OBBJECT"


def test_indicator_dimension_dropdowns(monkeypatch):
    assert asyncio.run(router_module.indicator_frequencies(_META, None)) == []
    assert asyncio.run(router_module.indicator_frequencies(_META, "ZZZ")) == []

    freqs = asyncio.run(router_module.indicator_frequencies(_META, "EXR"))
    assert any(o["value"] == "D" for o in freqs)

    areas = asyncio.run(router_module.indicator_areas(_META, "EXR"))
    assert areas and any(o["value"] == "USD" for o in areas)

    monkeypatch.setattr(
        _META, "get_dataflow_dimensions", lambda flow: [{"id": "FREQ", "values": []}]
    )
    assert asyncio.run(router_module.indicator_areas(_META, "EXR")) == []


_BSI_TABLE = "BSI01_01"


def test_table_listing_commands():
    tables = asyncio.run(router_module.list_tables(_META))
    assert tables and any(t["value"] == _BSI_TABLE for t in tables)

    all_choices = asyncio.run(router_module.list_table_choices(_META, None))
    assert any(c["value"] == _BSI_TABLE for c in all_choices)
    assert all(set(c) == {"label", "value"} for c in all_choices)

    bsi_choices = asyncio.run(router_module.list_table_choices(_META, "BSI"))
    assert bsi_choices and any(c["value"] == _BSI_TABLE for c in bsi_choices)
    assert len(bsi_choices) < len(all_choices)


def test_presentation_table(monkeypatch):
    from openbb_ecb.utils import query_builder

    assert asyncio.run(router_module.presentation_table(_META, "NOPE")) == []

    captured = {}

    async def _fetch(flow_ref, key, **kwargs):
        captured["flow"] = flow_ref
        captured["last_n"] = kwargs.get("last_n")
        return [
            {
                "series_key": "M.U2.X",
                "_dim_ids": ["FREQ", "ITEM"],
                "FREQ__label": "Monthly",
                "ITEM__label": "M3",
                "UNIT__label": "Euro",
                "UNIT_MULT": "6",
                "OBS_VALUE": 9.0,
                "date": "2024-01-01",
            }
        ]

    monkeypatch.setattr(query_builder, "fetch_sdmx_data", _fetch)
    monkeypatch.setattr(
        _META, "get_table_rows", lambda tid: [{"flow": "BSI", "key": "M.U2.X"}]
    )
    rows = asyncio.run(router_module.presentation_table(_META, _BSI_TABLE, limit=3))
    assert captured["flow"] == "BSI" and captured["last_n"] == 3
    assert rows[0]["2024-01-01"] == 9_000_000.0
    assert rows[0]["unit"] == "Euro" and "title" in rows[0]


def test_concept_commands():
    concepts = asyncio.run(router_module.list_concepts(_META))
    assert concepts and any(c["value"] == "bank-interest-rates" for c in concepts)

    choices = asyncio.run(router_module.concept_choices(_META))
    assert all(set(c) == {"label", "value"} for c in choices)
    assert any(c["value"] == "bank-interest-rates" for c in choices)

    all_flows = asyncio.run(router_module.dataflow_info_choices(_META, None))
    assert all_flows and all(set(c) == {"label", "value"} for c in all_flows)
    filtered = asyncio.run(
        router_module.dataflow_info_choices(_META, "bank-interest-rates")
    )
    assert [c["value"] for c in filtered] == ["MIR"]
    unknown = asyncio.run(router_module.dataflow_info_choices(_META, "does-not-exist"))
    assert len(unknown) == len(all_flows)


def test_dataflow_information():
    by_flow = asyncio.run(router_module.dataflow_information(dataflow="MIR"))
    body = by_flow.body.decode()
    assert "MIR</span>" in body and "<h2>Scope</h2>" in body
    by_concept = asyncio.run(
        router_module.dataflow_information(concept="bank-interest-rates")
    )
    assert "MIR</span>" in by_concept.body.decode()
    empty = asyncio.run(router_module.dataflow_information(concept="car-registrations"))
    assert "No data information" in empty.body.decode()
    missing = asyncio.run(router_module.dataflow_information(dataflow="NOPE_XYZ"))
    assert "No data information" in missing.body.decode()


def test_get_apps_json():
    apps = asyncio.run(router_module.get_ecb_apps_json())
    assert apps[0]["name"] == "ECB Explorer"
    assert "catalogue" in apps[0]["tabs"]


def _patch_feeds(monkeypatch, rss, html=None):
    from openbb_ecb.utils import data_cache, non_sdmx

    async def _passthrough(dataset, key, loader):
        return await loader()

    monkeypatch.setattr(non_sdmx, "fetch_rss_items", rss)
    monkeypatch.setattr(data_cache, "cached_records", _passthrough)
    if html is not None:
        monkeypatch.setattr(non_sdmx, "fetch_release_html", html)


def test_release_choices(monkeypatch):

    async def _rss(feed):
        return [
            {"date": "2026-06-20T10:00:00", "title": "Old", "url": "https://x/a"},
            {"date": "2026-06-24T10:00:00", "title": "New", "url": "https://x/b"},
            {"date": None, "title": "NoUrl", "url": ""},
        ]

    _patch_feeds(monkeypatch, _rss)
    out = asyncio.run(router_module.release_choices("blog"))
    assert [o["value"] for o in out] == ["https://x/b", "https://x/a"]
    assert out[0]["label"] == "2026-06-24 · New"
    assert asyncio.run(router_module.release_choices("bogus"))


def test_release_document(monkeypatch):

    async def _rss(feed):
        return [{"date": "2026-06-24T10:00:00", "title": "New", "url": "https://x/b"}]

    async def _html(url):
        return f"<html><body>ARTICLE {url}</body></html>"

    _patch_feeds(monkeypatch, _rss, _html)
    resp = asyncio.run(router_module.release_document(release="https://x/given"))
    assert resp.status_code == 200 and b"ARTICLE https://x/given" in resp.body
    resp2 = asyncio.run(router_module.release_document(release="", category="blog"))
    assert b"ARTICLE https://x/b" in resp2.body

    async def _empty(url):
        return ""

    _patch_feeds(monkeypatch, _rss, _empty)
    resp3 = asyncio.run(router_module.release_document(release="https://x/given"))
    assert b"No release content available" in resp3.body

    async def _empty_rss(feed):
        return []

    _patch_feeds(monkeypatch, _empty_rss, _empty)
    resp4 = asyncio.run(router_module.release_document(release="", category="bogus"))
    assert b"No release content available" in resp4.body


def test_get_apps_json_error(monkeypatch):

    def _raise(*args, **kwargs):
        raise ValueError("corrupt")

    monkeypatch.setattr(json, "load", _raise)
    assert asyncio.run(router_module.get_ecb_apps_json()) == []


def test_rewrite_widget_ids(monkeypatch):
    apps = [
        {
            "tabs": {
                "t": {
                    "layout": [
                        {"i": "ecb_exchange_rates_ecb_obb"},
                        {"i": "ecb_release_document"},
                    ]
                }
            }
        }
    ]
    monkeypatch.setattr(
        router_module,
        "_OWNER_WIDGET_MAP",
        {"ecb_exchange_rates_ecb_obb": "currency_price_historical_ecb_obb"},
    )
    out = router_module._rewrite_widget_ids(apps)
    ids = [item["i"] for item in out[0]["tabs"]["t"]["layout"]]
    assert ids == ["currency_price_historical_ecb_obb", "ecb_release_document"]

    monkeypatch.setattr(router_module, "_OWNER_WIDGET_MAP", {})
    assert router_module._rewrite_widget_ids(apps) is apps


def test_owner_installed_namespacing(monkeypatch):
    import importlib

    from openbb_ecb import _installed

    monkeypatch.setattr(_installed, "CURRENCY_INSTALLED", True)
    monkeypatch.setattr(_installed, "ECONOMY_INSTALLED", True)
    monkeypatch.setattr(_installed, "FIXEDINCOME_INSTALLED", True)
    try:
        reloaded = importlib.reload(router_module)
        owner_map = reloaded._OWNER_WIDGET_MAP
        assert "ecb_exchange_rates_ecb_obb" in owner_map
        assert "ecb_balance_of_payments_ecb_obb" in owner_map
        assert "ecb_available_indicators_ecb_obb" in owner_map
        assert "ecb_yield_curve_ecb_obb" in owner_map
        assert len(owner_map) == 9
    finally:
        monkeypatch.undo()
        importlib.reload(router_module)
