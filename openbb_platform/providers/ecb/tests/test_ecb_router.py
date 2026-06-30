"""Unit tests for ``openbb_ecb.ecb_router``."""

import asyncio
import json

from openbb_ecb import ecb_router as router_module
from openbb_ecb.utils.metadata import EcbMetadata

_META = EcbMetadata()


def test_list_and_search_dataflows():
    """Catalogue listing and search; an empty query lists every dataflow."""
    every = asyncio.run(router_module.list_dataflows(_META))
    assert any(d["value"] == "EXR" for d in every)
    assert any(
        d["value"] == "EXR"
        for d in asyncio.run(router_module.search_dataflows(_META, "exchange"))
    )
    # No query -> the full catalogue (the `dataflow` arg is a click-to-group target).
    assert len(asyncio.run(router_module.search_dataflows(_META, None))) == len(every)


def test_topics_commands():
    """Topic listing and topic->dataflows commands (rows render as a table)."""
    topics = asyncio.run(router_module.list_topics(_META))
    assert topics
    rows = asyncio.run(router_module.topic_dataflows(_META, topics[0]["value"]))
    assert rows
    # rows are dataflow records (dicts), not bare ids, so the widget can render.
    assert all(isinstance(r, dict) and "value" in r for r in rows)


def test_get_dataflow_dimensions():
    """Dimension discovery returns the EXR dimensions."""
    dims = asyncio.run(router_module.get_dataflow_dimensions(_META, "EXR"))
    assert [d["id"] for d in dims][0] == "FREQ"


def test_dimension_choices_no_selections():
    """Without selections the full codelist is returned."""
    out = asyncio.run(router_module.dimension_choices(_META, "EXR", "CURRENCY", None))
    assert out == _META.resolve_dimension_values("EXR", "CURRENCY")


def test_dimension_choices_narrowed(monkeypatch):
    """With selections, availability narrows the options."""
    monkeypatch.setattr(
        _META, "_fetch_available_constraint", lambda flow, key: {"CURRENCY": ["USD"]}
    )
    out = asyncio.run(
        router_module.dimension_choices(_META, "EXR", "CURRENCY", "FREQ=D,bare")
    )
    assert {o["value"] for o in out} == {"USD"}


def test_dimension_choices_no_availability(monkeypatch):
    """When availability is empty, the full codelist is returned."""
    monkeypatch.setattr(_META, "_fetch_available_constraint", lambda flow, key: {})
    out = asyncio.run(
        router_module.dimension_choices(_META, "EXR", "CURRENCY", "FREQ=D")
    )
    assert out == _META.resolve_dimension_values("EXR", "CURRENCY")


def test_model_commands(monkeypatch):
    """Every model-driven command delegates to OBBject.from_query."""

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
        router_module.releases,
        router_module.eligible_assets,
    ]
    for command in commands:
        result = asyncio.run(command(None, None, None, None))
        assert result[0] == "OBBJECT"


def test_indicator_dimension_dropdowns(monkeypatch):
    """``available_indicators`` frequency / reference-area dropdowns per dataflow."""
    assert asyncio.run(router_module.indicator_frequencies(_META, None)) == []
    assert asyncio.run(router_module.indicator_frequencies(_META, "ZZZ")) == []

    freqs = asyncio.run(router_module.indicator_frequencies(_META, "EXR"))
    assert any(o["value"] == "D" for o in freqs)  # EXR is daily

    areas = asyncio.run(router_module.indicator_areas(_META, "EXR"))
    assert areas and any(o["value"] == "USD" for o in areas)  # EXR geography = CURRENCY

    # A dataflow with no geography dimension -> no options.
    monkeypatch.setattr(
        _META, "get_dataflow_dimensions", lambda flow: [{"id": "FREQ", "values": []}]
    )
    assert asyncio.run(router_module.indicator_areas(_META, "EXR")) == []


_BSI_TABLE = "HCL_JDF_BSI_MFI_BALANCE_SHEET@HCL_BSI"


def test_table_listing_commands():
    """``list_tables`` / ``list_table_choices`` expose dataflow-backed tables."""
    tables = asyncio.run(router_module.list_tables(_META))
    assert tables and any(t["value"] == _BSI_TABLE for t in tables)

    all_choices = asyncio.run(router_module.list_table_choices(_META, None))
    assert any(c["value"] == _BSI_TABLE for c in all_choices)

    bsi_choices = asyncio.run(router_module.list_table_choices(_META, "BSI"))
    assert bsi_choices and all("BSI" in c["value"] for c in bsi_choices)
    assert len(bsi_choices) < len(all_choices)


def test_presentation_table_slice_choices(monkeypatch):
    """The frequency / reference-area dropdowns offer the table's valid values."""
    assert asyncio.run(router_module.presentation_table_frequencies(_META, None)) == []
    assert (
        asyncio.run(router_module.presentation_table_frequencies(_META, "NOPE")) == []
    )
    assert asyncio.run(router_module.presentation_table_areas(_META, None)) == []

    freqs = asyncio.run(router_module.presentation_table_frequencies(_META, _BSI_TABLE))
    assert {o["value"] for o in freqs} == set(
        _META.get_table_valid_context(_BSI_TABLE)["FREQ"]
    )
    areas = asyncio.run(router_module.presentation_table_areas(_META, _BSI_TABLE))
    assert areas and any(o["label"] == "Germany" for o in areas)

    # No candidate geography dimension in the valid context -> no options.
    monkeypatch.setattr(_META, "get_table_valid_context", lambda tid: {"FREQ": ["M"]})
    assert asyncio.run(router_module.presentation_table_areas(_META, _BSI_TABLE)) == []


def test_presentation_table(monkeypatch):
    """Resolves rows + values; frequency / reference area override the default slice."""
    from openbb_ecb.utils import query_builder

    assert asyncio.run(router_module.presentation_table(_META, "NOPE")) == []

    captured = {}

    async def _fetch(flow_ref, key, **kwargs):
        captured["key"] = key
        return [
            {
                "BS_ITEM": "A20",
                "BS_COUNT_SECTOR": "1000",
                "MATURITY_ORIG": "A",
                "OBS_VALUE": 9.0,
                "date": "2024-01-01",
                "series_key": "k",
            }
        ]

    monkeypatch.setattr(query_builder, "fetch_sdmx_data", _fetch)

    # No overrides -> the cached default slice (REF_AREA=U2) is used.
    rows = asyncio.run(router_module.presentation_table(_META, _BSI_TABLE))
    assert rows and any(r.get("2024-01-01") == 9.0 for r in rows)
    assert all("title" in r for r in rows)  # pivoted, indented title rows
    assert captured["key"].split(".")[:2] == ["M", "U2"]

    # Overriding frequency + reference area changes those key segments only.
    asyncio.run(
        router_module.presentation_table(
            _META, _BSI_TABLE, frequency="Q", reference_area="DE"
        )
    )
    assert captured["key"].split(".")[:2] == ["Q", "DE"]


def test_presentation_table_no_geography(monkeypatch):
    """A reference area is ignored when the table has no geography dimension."""
    from openbb_ecb.utils import query_builder

    captured = {}

    async def _fetch(flow_ref, key, **kwargs):
        captured["key"] = key
        return []

    monkeypatch.setattr(query_builder, "fetch_sdmx_data", _fetch)
    monkeypatch.setattr(_META, "get_table_valid_context", lambda tid: {"FREQ": ["M"]})
    asyncio.run(
        router_module.presentation_table(_META, _BSI_TABLE, reference_area="DE")
    )
    assert "DE" not in captured["key"].split(".")


def test_get_apps_json():
    """The bundled apps.json is served."""
    apps = asyncio.run(router_module.get_ecb_apps_json())
    assert apps[0]["name"] == "ECB Explorer"
    assert "catalogue" in apps[0]["tabs"]


def test_get_apps_json_error(monkeypatch):
    """A corrupt/unreadable apps.json yields an empty list."""

    def _raise(*args, **kwargs):
        raise ValueError("corrupt")

    monkeypatch.setattr(json, "load", _raise)
    assert asyncio.run(router_module.get_ecb_apps_json()) == []


def test_rewrite_widget_ids(monkeypatch):
    """Widget ids are remapped to owner namespaces when the map is populated."""
    apps = [
        {
            "tabs": {
                "t": {
                    "layout": [
                        {"i": "ecb_exchange_rates_ecb_obb"},
                        {"i": "ecb_releases_ecb_obb"},
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
    assert ids == ["currency_price_historical_ecb_obb", "ecb_releases_ecb_obb"]

    monkeypatch.setattr(router_module, "_OWNER_WIDGET_MAP", {})
    assert router_module._rewrite_widget_ids(apps) is apps


def test_owner_installed_namespacing(monkeypatch):
    """With owners installed, the owner widget map fills and commands defer."""
    import importlib

    from openbb_ecb import _installed

    monkeypatch.setattr(_installed, "CURRENCY_INSTALLED", True)
    monkeypatch.setattr(_installed, "ECONOMY_INSTALLED", True)
    monkeypatch.setattr(_installed, "FIXEDINCOME_INSTALLED", True)
    try:
        reloaded = importlib.reload(router_module)
        owner_map = reloaded._OWNER_WIDGET_MAP
        assert "ecb_exchange_rates_ecb_obb" in owner_map  # currency
        assert "ecb_balance_of_payments_ecb_obb" in owner_map  # economy
        assert "ecb_available_indicators_ecb_obb" in owner_map  # economy
        assert "ecb_yield_curve_ecb_obb" in owner_map  # fixedincome
        assert len(owner_map) == 9
    finally:
        monkeypatch.undo()
        importlib.reload(router_module)
