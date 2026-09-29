"""Shared fixtures for the OECD test suite."""

from __future__ import annotations

import pytest

from openbb_oecd.utils.metadata import OecdMetadata

_FULL_ID = "DSD_TEST@DF_TEST"
_SHORT_ID = "DF_TEST"

_TEST_DATAFLOW = {
    "id": _FULL_ID,
    "short_id": _SHORT_ID,
    "agency_id": "OECD",
    "version": "1.0",
    "name": "Test Dataflow",
    "description": "",
    "structure_ref": "",
}

_TEST_DSD = {
    "dsd_id": "DSD_TEST",
    "agency_id": "OECD",
    "version": "1.0",
    "dimensions": [
        {
            "id": "REF_AREA",
            "position": 1,
            "codelist_id": "OECD:CL_AREA(1.0)",
            "concept_id": "REF_AREA",
            "name": "Reference Area",
        },
        {
            "id": "MEASURE",
            "position": 2,
            "codelist_id": "OECD:CL_MEASURE(1.0)",
            "concept_id": "MEASURE",
            "name": "Measure",
        },
        {
            "id": "FREQ",
            "position": 3,
            "codelist_id": "OECD:CL_FREQ(1.0)",
            "concept_id": "FREQ",
            "name": "Frequency",
        },
    ],
    "attributes": [],
    "has_time_dimension": True,
}

_TEST_CODELISTS = {
    "OECD:CL_AREA(1.0)": {
        "USA": "United States",
        "GBR": "United Kingdom",
        "DEU": "Germany",
    },
    "OECD:CL_MEASURE(1.0)": {
        "CPI": "Consumer Price Index",
        "PPI": "Producer Price Index",
    },
    "OECD:CL_FREQ(1.0)": {"A": "Annual", "Q": "Quarterly", "M": "Monthly"},
}

_TEST_CONSTRAINTS = {
    _FULL_ID: {
        "REF_AREA": ["USA", "GBR"],
        "MEASURE": ["CPI"],
        "FREQ": ["A", "Q"],
    }
}


@pytest.fixture
def seeded_meta(monkeypatch):
    """Fresh OecdMetadata singleton with test data pre-loaded, no I/O."""
    OecdMetadata._reset()
    monkeypatch.setattr(OecdMetadata, "_load_from_cache", lambda self: True)
    instance = OecdMetadata()
    instance.dataflows[_FULL_ID] = _TEST_DATAFLOW.copy()
    instance._short_id_map[_SHORT_ID] = _FULL_ID
    instance._full_catalogue_loaded = True
    instance.datastructures[_FULL_ID] = {
        "dsd_id": "DSD_TEST",
        "agency_id": "OECD",
        "version": "1.0",
        "dimensions": [dict(d) for d in _TEST_DSD["dimensions"]],
        "attributes": [],
        "has_time_dimension": True,
    }
    instance.codelists.update({k: dict(v) for k, v in _TEST_CODELISTS.items()})
    instance._dataflow_constraints.update(
        {
            k: {dk: list(dv) for dk, dv in v.items()}
            for k, v in _TEST_CONSTRAINTS.items()
        }
    )
    yield instance
    OecdMetadata._reset()


@pytest.fixture
def empty_meta(monkeypatch):
    """Fresh OecdMetadata singleton with nothing loaded (and no I/O)."""
    OecdMetadata._reset()
    monkeypatch.setattr(OecdMetadata, "_load_from_cache", lambda self: True)
    inst = OecdMetadata()
    yield inst
    OecdMetadata._reset()
