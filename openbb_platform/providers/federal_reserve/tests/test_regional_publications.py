"""Tests for the fedinprint-backed regional publications across Reserve Banks."""

import pytest
from openbb_core.provider.utils.errors import EmptyDataError

import openbb_federal_reserve as provider
from openbb_federal_reserve.utils import fedinprint

_FD = provider.federal_reserve_provider.fetcher_dict

DISTRICTS = {
    "atlanta": "Atlanta",
    "boston": "Boston",
    "chicago": "Chicago",
    "cleveland": "Cleveland",
    "dallas": "Dallas",
    "kc": "KansasCity",
    "minneapolis": "Minneapolis",
    "ny": "NewYork",
    "philadelphia": "Philadelphia",
    "richmond": "Richmond",
    "sf": "SanFrancisco",
}

_CATALOG = [
    {"series": "WP", "date": "2026-06-01", "title": "New", "url": "https://x/new.pdf"},
    {"series": "WP", "date": "2024-01-01", "title": "Old", "url": "https://x/old.pdf"},
]


@pytest.mark.parametrize("district, prefix", list(DISTRICTS.items()))
class TestRegionalPublications:
    """Every migrated bank's publications + series models run through fedinprint."""

    def test_publications_delegates(self, monkeypatch, district, prefix):
        """extract_data forwards the district and paging to fedinprint."""
        captured = {}

        def _list(dist, series=None, start_date=None, start=0, limit=20):
            captured.update(district=dist, start=start, limit=limit)
            return _CATALOG

        monkeypatch.setattr(fedinprint, "list_publications", _list)
        fetcher = _FD[f"FederalReserve{prefix}Publications"]
        query = fetcher.transform_query({"limit": 5, "offset": 10})
        rows = fetcher.transform_data(query, fetcher.extract_data(query, None))
        assert captured["district"] == district
        assert (captured["start"], captured["limit"]) == (10, 5)
        assert rows[0].url == "https://x/new.pdf"
        assert not hasattr(rows[0], "id")

    def test_publications_date_filter(self, monkeypatch, district, prefix):
        """The transform_data start_date and end_date filters narrow the catalog."""
        monkeypatch.setattr(fedinprint, "list_publications", lambda *a, **k: _CATALOG)
        fetcher = _FD[f"FederalReserve{prefix}Publications"]
        start_query = fetcher.transform_query({"start_date": "2026-01-01"})
        start_rows = fetcher.transform_data(
            start_query, fetcher.extract_data(start_query, None)
        )
        assert [r.title for r in start_rows] == ["New"]
        end_query = fetcher.transform_query({"end_date": "2025-01-01"})
        end_rows = fetcher.transform_data(
            end_query, fetcher.extract_data(end_query, None)
        )
        assert [r.title for r in end_rows] == ["Old"]

    def test_publications_empty_raises(self, monkeypatch, district, prefix):
        """An empty catalog raises EmptyDataError."""
        monkeypatch.setattr(fedinprint, "list_publications", lambda *a, **k: [])
        fetcher = _FD[f"FederalReserve{prefix}Publications"]
        query = fetcher.transform_query({})
        with pytest.raises(EmptyDataError):
            fetcher.extract_data(query, None)

    def test_series_options_match_registry(self, district, prefix):
        """The series options list every registry slug for the district."""
        fetcher = _FD[f"FederalReserve{prefix}Publications"]
        params = type(fetcher.transform_query({}))
        options = params.__json_schema_extra__["series"]["x-widget_config"]["options"]
        slugs = [slug for slug, _ in fedinprint.load_registry()[district]["series"]]
        assert [option["value"] for option in options] == slugs

    def test_publication_series_lists_registry(self, monkeypatch, district, prefix):
        """publication_series returns the district's supported series."""
        monkeypatch.setattr(
            fedinprint,
            "list_series",
            lambda dist: [
                {"series": "working_papers", "name": "Working Papers", "count": 5}
            ],
        )
        fetcher = _FD[f"FederalReserve{prefix}PublicationSeries"]
        query = fetcher.transform_query({})
        rows = fetcher.transform_data(query, fetcher.extract_data(query, None))
        assert rows[0].series == "working_papers"
        assert rows[0].count == 5

    def test_publication_series_empty_raises(self, monkeypatch, district, prefix):
        """An empty series list raises EmptyDataError."""
        monkeypatch.setattr(fedinprint, "list_series", lambda dist: [])
        fetcher = _FD[f"FederalReserve{prefix}PublicationSeries"]
        query = fetcher.transform_query({})
        with pytest.raises(EmptyDataError):
            fetcher.extract_data(query, None)
