"""Tests for ``openbb_government_ca.government_ca_router``.

The router exposes the ``available_indicators`` model command plus
two helper endpoints (``list_cube_choices`` and
``list_subject_choices``) for populating UI dropdowns and parameter
Literal types.

The Router class from openbb_core is not directly mountable on a
bare FastAPI app (it relies on the OpenBB platform wiring), so these
tests exercise the underlying handler functions directly with a
seeded metadata singleton.
"""

from __future__ import annotations

from openbb_government_ca.government_ca_router import (
    list_cube_choices,
    list_subject_choices,
)
from openbb_government_ca.utils.metadata import GovernmentCaMetadata


def _seed_catalog() -> None:
    """Populate the singleton with a minimal SDMX catalog."""
    GovernmentCaMetadata._reset()
    meta = GovernmentCaMetadata()
    meta._apply_blob(
        {
            "boc": {},
            "statscan": {
                "status": "ok",
                "indicators": [],
                "catalog": {
                    "cubes": {
                        "10100139": {
                            "pid": "10100139",
                            "title_en": "GDP",
                            "subject_code": "13",
                            "frequency_code": "6",
                            "series": [],
                        },
                        "20100008": {
                            "pid": "20100008",
                            "title_en": "CPI",
                            "subject_code": "14",
                            "frequency_code": "6",
                            "series": [],
                        },
                    },
                    "subjects": {
                        "13": "Economic accounts",
                        "14": "Consumer prices",
                    },
                    "cube_count": 2,
                    "series_count": 0,
                    "status": "ok",
                },
            },
        }
    )


class TestListCubeChoices:
    """``list_cube_choices`` returns the catalog cubes."""

    def test_list_all_cubes_when_no_query(self):
        """Without a query filter, every cube is returned."""
        _seed_catalog()
        try:
            meta = GovernmentCaMetadata()
            obbject = list_cube_choices(meta, query=None)
            pids = {row["pid"] for row in obbject.results}
            assert pids == {"10100139", "20100008"}
        finally:
            GovernmentCaMetadata._reset()

    def test_filter_by_query_substring(self):
        """A case-insensitive substring filter narrows the results."""
        _seed_catalog()
        try:
            meta = GovernmentCaMetadata()
            obbject = list_cube_choices(meta, query="gdp")
            pids = {row["pid"] for row in obbject.results}
            assert pids == {"10100139"}
        finally:
            GovernmentCaMetadata._reset()

    def test_empty_catalog_returns_empty_list(self):
        """An empty catalog returns an empty results list."""
        GovernmentCaMetadata._reset()
        meta = GovernmentCaMetadata()
        meta._apply_blob({"boc": {}, "statscan": {"status": "ok"}})
        try:
            obbject = list_cube_choices(meta, query=None)
            assert obbject.results == []
        finally:
            GovernmentCaMetadata._reset()


class TestListSubjectChoices:
    """``list_subject_choices`` returns the subjects dict."""

    def test_list_subjects(self):
        """Every subject in the catalog is returned as a row."""
        _seed_catalog()
        try:
            meta = GovernmentCaMetadata()
            obbject = list_subject_choices(meta)
            codes = {row["subject_code"] for row in obbject.results}
            assert codes == {"13", "14"}
        finally:
            GovernmentCaMetadata._reset()
