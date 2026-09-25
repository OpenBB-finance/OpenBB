"""Shared pytest fixtures for the IMF provider."""

from __future__ import annotations

from typing import Any

import pytest


@pytest.fixture(autouse=True)
def _reset_imf_metadata_singleton() -> Any:
    """Drop the ``ImfMetadata`` singleton before and after each test."""
    from openbb_imf.utils.metadata import ImfMetadata

    ImfMetadata._reset()
    yield
    ImfMetadata._reset()


def _reset_alru(fn: Any) -> None:
    """Clear an ``alru_cache`` wrapper and reset its event-loop binding."""
    if hasattr(fn, "cache_clear"):
        fn.cache_clear()
    for attr in ("_LRUCacheWrapper__first_loop", "_LRUCacheWrapper__warned_loop_reset"):
        if hasattr(fn, attr):
            setattr(fn, attr, None if "first_loop" in attr else False)


@pytest.fixture(autouse=True)
def _clear_alru_caches() -> Any:
    """Clear every ``alru_cache``-wrapped helper between tests."""
    from openbb_imf.utils import port_watch_helpers as pwh

    targets = [
        pwh.get_daily_chokepoint_data,
        pwh.get_all_daily_chokepoint_activity_data,
        pwh.get_all_daily_port_activity_data,
        pwh.get_daily_port_activity_data,
        pwh.list_ports,
        pwh.get_country_daily_activity,
        pwh.get_monthly_trade,
        pwh.get_container_metrics,
        pwh.get_disruption_events,
        pwh.get_disruption_sankey_edges,
        pwh.get_container_port_name_map,
    ]
    for fn in targets:
        _reset_alru(fn)
    yield
    for fn in targets:
        _reset_alru(fn)


@pytest.fixture
def empty_meta(monkeypatch: pytest.MonkeyPatch) -> Any:
    """Fresh ``ImfMetadata`` singleton with cache loading disabled."""
    from openbb_imf.utils.metadata import ImfMetadata

    ImfMetadata._reset()
    monkeypatch.setattr(ImfMetadata, "_load_from_cache", lambda self: True)
    instance = ImfMetadata()
    yield instance
    ImfMetadata._reset()


@pytest.fixture
def seeded_meta(monkeypatch: pytest.MonkeyPatch) -> Any:
    """Fresh ``ImfMetadata`` with a minimal in-memory fixture catalog."""
    from openbb_imf.utils.metadata import ImfMetadata

    ImfMetadata._reset()
    monkeypatch.setattr(ImfMetadata, "_load_from_cache", lambda self: True)
    instance = ImfMetadata()

    instance.dataflows = {
        "TEST_DF": {
            "id": "TEST_DF",
            "agencyID": "IMF.STA",
            "name": "Test Dataflow",
            "description": "",
            "structureRef": {"id": "DSD_TEST"},
        }
    }
    instance.datastructures = {
        "DSD_TEST": {
            "id": "DSD_TEST",
            "agencyID": "IMF.STA",
            "dimensions": [
                {"id": "COUNTRY", "position": "0", "conceptRef": {"id": "COUNTRY"}},
                {"id": "FREQUENCY", "position": "1", "conceptRef": {"id": "FREQ"}},
                {"id": "INDICATOR", "position": "2", "conceptRef": {"id": "INDICATOR"}},
            ],
        }
    }
    instance._codelist_cache = {
        "CL_COUNTRY": {
            "USA": "United States",
            "GBR": "United Kingdom",
            "DEU": "Germany",
        },
        "CL_FREQ": {"A": "Annual", "Q": "Quarterly", "M": "Monthly"},
        "CL_INDICATOR": {
            "GDP": "Gross Domestic Product",
            "CPI": "Consumer Price Index",
            "POP": "Population",
        },
    }
    instance._codelist_descriptions = {
        "CL_COUNTRY": {"USA": "USA", "GBR": "UK", "DEU": "DE"},
        "CL_FREQ": {"A": "Annual", "Q": "Quarterly", "M": "Monthly"},
        "CL_INDICATOR": {"GDP": "GDP", "CPI": "CPI", "POP": "Population"},
    }
    yield instance
    ImfMetadata._reset()
