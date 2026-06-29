"""Shared fixtures for the openbb-government-ca test suite.

Mirrors the OECD V5 conftest pattern: fixtures build a fresh
singleton with a pre-seeded cache blob and monkey-patch out the
cache loader so tests never touch the filesystem or network.
"""

from __future__ import annotations

import pytest

from openbb_government_ca.utils.metadata import GovernmentCaMetadata

# A small but realistic seed blob covering both sub-namespaces. The
# shape mirrors what the real cache generator produces, so tests that
# exercise ``lookup_series`` / ``lookup_product`` can rely on real
# key names.
_SEED_BLOB = {
    "generated_at": "2026-06-28T04:17:00Z",
    "source": "test-fixture",
    "boc": {
        "valet_url": "https://www.bankofcanada.ca/valet",
        "series_count": 5,
        "groups_count": 1,
        "status": "ok",
        "series": {
            "FXUSDCAD": {
                "name": "FXUSDCAD",
                "label": "USD/CAD",
                "tenor": None,
                "tenor_years": None,
                "description": (
                    "Daily average exchange rate: daily value of the US dollar "
                    "expressed in Canadian dollars, for 1 unit of US dollar"
                ),
                "frequency": "daily",
                "link": "https://www.bankofcanada.ca/valet/series/FXUSDCAD",
                "observations_url": (
                    "https://www.bankofcanada.ca/valet/observations/FXUSDCAD/json"
                ),
                "cataloged_at": "2026-06-28T04:17:00Z",
            },
            "V39079": {
                "name": "V39079",
                "label": "V39079",
                "description": "Target for the overnight rate",
                "tenor": None,
                "tenor_years": None,
                "frequency": "daily",
                "link": "https://www.bankofcanada.ca/valet/series/V39079",
                "observations_url": (
                    "https://www.bankofcanada.ca/valet/observations/V39079/json"
                ),
                "cataloged_at": "2026-06-28T04:17:00Z",
            },
            "CBC20210": {
                "name": "CBC20210",
                "label": "V39079",
                "description": "Target for the overnight rate",
                "tenor": None,
                "tenor_years": None,
                "frequency": "daily",
                "link": "https://www.bankofcanada.ca/valet/series/CBC20210",
                "observations_url": (
                    "https://www.bankofcanada.ca/valet/observations/CBC20210/json"
                ),
                "cataloged_at": "2026-06-28T04:17:00Z",
            },
            "V39078": {
                "name": "V39078",
                "label": "V39078",
                "description": "Bank rate",
                "tenor": None,
                "tenor_years": None,
                "frequency": "daily",
                "link": "https://www.bankofcanada.ca/valet/series/V39078",
                "observations_url": (
                    "https://www.bankofcanada.ca/valet/observations/V39078/json"
                ),
                "cataloged_at": "2026-06-28T04:17:00Z",
            },
            "BD.CDN.10YR.DQ.YLD": {
                "name": "BD.CDN.10YR.DQ.YLD",
                "label": "Benchmark bond yield: 10 year",
                "description": "Benchmark bond yield: 10 year",
                "frequency": "daily",
                "tenor": "10Y",
                "tenor_years": 10,
                "link": "https://www.bankofcanada.ca/valet/series/BD.CDN.10YR.DQ.YLD",
                "observations_url": (
                    "https://www.bankofcanada.ca/valet/observations/"
                    "BD.CDN.10YR.DQ.YLD/json"
                ),
                "cataloged_at": "2026-06-28T04:17:00Z",
            },
        },
        "groups": {
            "FX_RATES_DAILY": {
                "name": "FX_RATES_DAILY",
                "label": "Daily exchange rates",
                "description": (
                    "The daily average exchange rates for various foreign currencies."
                ),
                "members": [
                    "FXAUDCAD",
                    "FXCNYCAD",
                    "FXEURCAD",
                    "FXGBPCAD",
                    "FXINRCAD",
                    "FXJPYCAD",
                    "FXMXNCAD",
                    "FXUSDCAD",
                ],
                "members_url": (
                    "https://www.bankofcanada.ca/valet/groups/FX_RATES_DAILY/json"
                ),
                "observations_url": (
                    "https://www.bankofcanada.ca/valet/observations/"
                    "group/FX_RATES_DAILY/json"
                ),
                "cataloged_at": "2026-06-28T04:17:00Z",
            },
        },
    },
    "statscan": {
        "homepage_url": (
            "https://www150.statcan.gc.ca/n1/dai-quo/ssi/homepage/ind-econ.json"
        ),
        "indicators": [
            {
                "registry_number": "3612",
                "indicator_number": "1",
                "geo_code": "0",
                "title_en": "Imports",
                "title_fr": "Importations",
                "value_en": "$47.6 billion",
                "value_fr": "47,6 milliards de dollars",
                "refper_en": "September 2016",
                "refper_fr": "Septembre 2016",
                "source": "2280069",
                "release_date": "2016-11-04",
                "growth_en": "4.7%",
                "growth_arrow": "1",
                "growth_details_en": "(monthly change)",
                "observations_url": (
                    "https://www150.statcan.gc.ca/t1/wds/rest/getDataVector"
                    "?vectorId=2280069&startRefPeriod=0&endReferencePeriod=0"
                ),
            },
            {
                "registry_number": "3587",
                "indicator_number": "1",
                "geo_code": "0",
                "title_en": "Employment",
                "title_fr": "Emploi",
                "value_en": "18,161,000",
                "value_fr": "18 161 000",
                "refper_en": "October 2016",
                "refper_fr": "Octobre 2016",
                "source": "2820087",
                "release_date": "2016-11-04",
                "growth_en": "0.2%",
                "growth_arrow": "1",
                "growth_details_en": "(monthly change)",
                "observations_url": (
                    "https://www150.statcan.gc.ca/t1/wds/rest/getDataVector"
                    "?vectorId=2820087&startRefPeriod=0&endReferencePeriod=0"
                ),
            },
        ],
        "geo_lookup": {"0": "Canada", "1": "Newfoundland and Labrador"},
        "themes_en": {"920": "Agriculture", "2239": "Business performance"},
        "themes_fr": {"920": "Agriculture"},
        "indicator_count": 2,
        "status": "ok",
    },
}


@pytest.fixture
def seeded_meta(monkeypatch):
    """Fresh ``GovernmentCaMetadata`` singleton with the seed blob pre-loaded.

    No filesystem I/O, no network. The monkey-patch replaces
    ``_load_from_cache`` so the singleton's ``__init__`` doesn't try
    to read the shipped cache file (which doesn't exist in the test
    environment).
    """
    GovernmentCaMetadata._reset()
    monkeypatch.setattr(GovernmentCaMetadata, "_load_from_cache", lambda self: True)
    instance = GovernmentCaMetadata()
    instance._apply_blob(_SEED_BLOB)
    yield instance
    GovernmentCaMetadata._reset()


@pytest.fixture
def empty_meta(monkeypatch):
    """Fresh ``GovernmentCaMetadata`` singleton with nothing loaded.

    Useful for testing error paths (``KeyError`` on lookup).
    """
    GovernmentCaMetadata._reset()
    monkeypatch.setattr(GovernmentCaMetadata, "_load_from_cache", lambda self: True)
    inst = GovernmentCaMetadata()
    yield inst
    GovernmentCaMetadata._reset()


@pytest.fixture
def seed_blob():
    """The seed cache blob — exposed for tests that want to assert on shape."""
    return _SEED_BLOB
