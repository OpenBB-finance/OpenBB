"""Tests for the Boston Fed NEEI/NEEC helpers and publication index."""

import base64
import json
from unittest.mock import MagicMock

import pytest
from openbb_core.app.model.abstract.error import OpenBBError

from openbb_federal_reserve.utils import boston, boston_publications


def _island(label: str, series: list[dict]) -> str:
    """Build a chart island anchor plus its base64 series-data div."""
    encoded = base64.b64encode(json.dumps(series).encode("utf-8")).decode("utf-8")
    return f'<a href="#">{label}</a><div class="hidden series-data">{encoded}</div>'


_GOOD = [
    {
        "name": "USRA",
        "description": "Unemployment Rate, United States (SA, %)",
        "originalFrequency": 40,
        "func": None,
        "sourceName": "BLS/Haver",
        "dataPoints": [{"date": "2026-05-01", "nSeriesData": 4.1}],
    }
]


class TestParseIslands:
    """Tests for ``parse_islands``."""

    def test_decodes_and_keys_by_label(self):
        """A base64 series-data div decodes and keys by its preceding label."""
        html = "<html>" + _island("Unemployment Rates", _GOOD) + "</html>"
        islands = boston.parse_islands(html)
        assert "Unemployment Rates" in islands
        assert islands["Unemployment Rates"][0]["name"] == "USRA"

    def test_skips_unlabeled_block(self):
        """A series-data div with no preceding anchor is skipped."""
        encoded = base64.b64encode(json.dumps(_GOOD).encode()).decode()
        html = f'<div class="hidden series-data">{encoded}</div>'
        assert boston.parse_islands(html) == {}

    def test_skips_invalid_base64(self):
        """A series-data div with undecodable content is skipped."""
        html = '<a href="#">X</a><div class="hidden series-data">@@@@</div>'
        assert boston.parse_islands(html) == {}


class TestFetchIndicator:
    """Tests for ``fetch_indicator``."""

    def test_unknown_indicator_raises(self):
        """An unknown indicator raises ``OpenBBError``."""
        with pytest.raises(OpenBBError):
            boston.fetch_indicator("nope")

    def test_unknown_geography_raises(self):
        """An unknown geography raises ``OpenBBError``."""
        with pytest.raises(OpenBBError):
            boston.fetch_indicator("consumer_price_index", "zz")

    def test_returns_records(self, monkeypatch):
        """A matched indicator/geography returns observation records."""
        html = "<html>" + _island("Unemployment Rates", _GOOD) + "</html>"
        monkeypatch.setattr(boston, "fetch_page", lambda: html)
        records = boston.fetch_indicator("unemployment_rates", "us")
        assert records[0]["value"] == 4.1
        assert records[0]["frequency"] == "monthly"
        assert records[0]["geography"] == "us"

    def test_missing_island_returns_empty(self, monkeypatch):
        """A page without the requested island yields no records."""
        monkeypatch.setattr(boston, "fetch_page", lambda: "<html></html>")
        assert boston.fetch_indicator("consumer_price_index", "us") == []


class TestFetchPage:
    """Tests for the patchable ``fetch_page`` HTTP helper."""

    def test_returns_text(self, monkeypatch):
        """``fetch_page`` returns the response body text."""
        response = MagicMock()
        response.text = "<html>ok</html>"
        response.raise_for_status = MagicMock()
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request",
            lambda *a, **k: response,
        )
        assert boston.fetch_page() == "<html>ok</html>"


def _pub_request(url, *args, **kwargs):
    """Fake make_request: real PDF only for even months, soft-404 otherwise."""
    response = MagicMock()
    response.raise_for_status = MagicMock()
    month = url.rsplit("/", 1)[-1][4:6]
    if month in {"04", "06"} and "2026" in url:
        response.content = b"%PDF-1.7 boston"
    else:
        response.content = b"\xef\xbb\xbf<!doctype html>"
    return response


class TestListPublications:
    """Tests for ``list_publications``."""

    def test_constructs_and_verifies(self, monkeypatch):
        """Only URLs answering with a real PDF enter the catalog, newest first."""
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request", _pub_request
        )
        monkeypatch.setattr(boston_publications, "NEEC_START_YEAR", 2026)
        catalog = boston_publications.list_publications()
        ids = [record["id"] for record in catalog]
        assert ids == ["202606", "202604"]
        assert catalog[0]["title"] == "New England Economic Conditions June 2026"
        assert catalog[0]["url"].endswith("202606NEEC.pdf")

    def test_skips_fetch_errors(self, monkeypatch):
        """A URL that raises on fetch is skipped without failing the catalog."""

        def _raising(url, *args, **kwargs):
            """Raise for May, return a real PDF for June."""
            if url.rsplit("/", 1)[-1][4:6] == "06" and "2026" in url:
                response = MagicMock()
                response.raise_for_status = MagicMock()
                response.content = b"%PDF-1.7 boston"
                return response
            raise RuntimeError("network down")

        monkeypatch.setattr("openbb_core.provider.utils.helpers.make_request", _raising)
        monkeypatch.setattr(boston_publications, "NEEC_START_YEAR", 2026)
        catalog = boston_publications.list_publications()
        assert [record["id"] for record in catalog] == ["202606"]

    def test_unknown_series_raises(self):
        """An unsupported series raises ``OpenBBError``."""
        with pytest.raises(OpenBBError):
            boston_publications.list_publications("workingpapers")


class TestFetchPublicationPdf:
    """Tests for ``fetch_publication_pdf``."""

    _CATALOG = [
        {
            "series": "neec",
            "id": "202606",
            "date": "2026-06-01",
            "title": "New England Economic Conditions June 2026",
            "url": "https://x/202606NEEC.pdf",
        },
        {
            "series": "neec",
            "id": "202604",
            "date": "2026-04-01",
            "title": "New England Economic Conditions April 2026",
            "url": "https://x/202604NEEC.pdf",
        },
    ]

    def _patch(self, monkeypatch):
        """Point the PDF fetch at a synthetic catalog and PDF bytes."""
        monkeypatch.setattr(
            boston_publications,
            "list_publications",
            lambda series="neec": list(self._CATALOG),
        )
        monkeypatch.setattr(
            boston_publications, "fetch_bytes", lambda url: b"%PDF-1.7 boston"
        )

    def test_latest(self, monkeypatch):
        """With no selector the latest issue downloads as a base64 PDF."""
        self._patch(monkeypatch)
        out = boston_publications.fetch_publication_pdf()
        assert out["data_format"]["filename"] == "Boston_NEEC_202606.pdf"
        assert base64.b64decode(out["content"]).startswith(b"%PDF")

    def test_by_date(self, monkeypatch):
        """A requested date selects the issue in that month."""
        self._patch(monkeypatch)
        out = boston_publications.fetch_publication_pdf(date="2026-04")
        assert out["data_format"]["filename"] == "Boston_NEEC_202604.pdf"

    def test_unknown_date_raises(self, monkeypatch):
        """A missing date raises ``OpenBBError``."""
        self._patch(monkeypatch)
        with pytest.raises(OpenBBError):
            boston_publications.fetch_publication_pdf(date="1999-01")

    def test_empty_catalog_raises(self, monkeypatch):
        """An empty catalog raises ``OpenBBError``."""
        monkeypatch.setattr(
            boston_publications, "list_publications", lambda series="neec": []
        )
        with pytest.raises(OpenBBError):
            boston_publications.fetch_publication_pdf()
