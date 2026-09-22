"""Tests for the Workspace-facing helpers in openbb_nasdaq.utils.helpers."""

import asyncio
from datetime import date

import pytest

from openbb_nasdaq.utils import helpers


class _Item:
    """Stand-in for a fetched model with a ``model_dump``."""

    def __init__(self, **fields):
        self._fields = fields

    def model_dump(self) -> dict:
        """Return the record."""
        return self._fields


class TestSymbolChoices:
    """Cover the symbol picker choices."""

    def test_excludes_non_operating_issues(self, monkeypatch):
        """Test issues, ETFs, and non-common classes are left out."""
        directory = [
            _Item(
                symbol="AAPL", name="Apple Inc. Common Stock", test_issue="N", etf="N"
            ),
            _Item(symbol="ZTEST", name="Test Issue", test_issue="Y", etf="N"),
            _Item(symbol="QQQ", name="Invesco QQQ", test_issue="N", etf="Y"),
            _Item(symbol="ABC.U", name="ABC Unit", test_issue="N", etf="N"),
            _Item(
                symbol="XYZP", name="XYZ Preferred Series A", test_issue="N", etf="N"
            ),
        ]

        async def _fetch(params, credentials):
            return directory

        monkeypatch.setattr(
            "openbb_nasdaq.models.equity_search.NasdaqEquitySearchFetcher.fetch_data",
            _fetch,
        )
        choices = asyncio.run(helpers.get_symbol_choices())

        assert [c["value"] for c in choices] == ["AAPL"]
        assert choices[0]["extraInfo"]["description"].startswith("Apple")


class TestIndexSymbolChoices:
    """Cover the index picker choices."""

    def test_builds_labels_from_the_index_directory(self, monkeypatch):
        """Every indexed symbol becomes a labelled choice."""
        directory = [
            _Item(symbol="COMP", name="Nasdaq Composite Index"),
            _Item(symbol=None, name="Unlisted"),
        ]

        async def _fetch(params, credentials):
            return directory

        monkeypatch.setattr(
            "openbb_nasdaq.models.index_search.NasdaqIndexSearchFetcher.fetch_data",
            _fetch,
        )
        choices = asyncio.run(helpers.get_index_symbol_choices())

        assert choices == [
            {
                "value": "COMP",
                "label": "COMP",
                "extraInfo": {"description": "Nasdaq Composite Index"},
            }
        ]


class TestEtfSymbolChoices:
    """Cover the fund picker choices."""

    def test_builds_labels_from_the_fund_directory(self, monkeypatch):
        """Every fund symbol becomes a labelled choice."""
        directory = [
            _Item(symbol="QQQ", name="Invesco QQQ Trust"),
            _Item(symbol=None, name="Unlisted"),
        ]

        async def _fetch(params, credentials):
            return directory

        monkeypatch.setattr(
            "openbb_nasdaq.models.etf_search.NasdaqEtfSearchFetcher.fetch_data",
            _fetch,
        )
        choices = asyncio.run(helpers.get_etf_symbol_choices())

        assert choices == [
            {
                "value": "QQQ",
                "label": "QQQ",
                "extraInfo": {"description": "Invesco QQQ Trust"},
            }
        ]


class TestDocumentChoices:
    """Cover the filing picker choices."""

    def test_without_a_symbol(self):
        """No symbol yields no choices."""
        assert asyncio.run(helpers.get_document_choices()) == []

    def test_builds_labels(self, monkeypatch):
        """Each filing with a PDF becomes a labelled choice."""
        filings = [
            _Item(filing_date=date(2026, 7, 24), pdf_url="https://x/a.pdf"),
            _Item(filing_date=date(2026, 7, 20), pdf_url=None),
        ]

        async def _fetch(params, credentials):
            return filings

        monkeypatch.setattr(
            "openbb_nasdaq.models.company_filings.NasdaqCompanyFilingsFetcher.fetch_data",
            _fetch,
        )
        choices = asyncio.run(helpers.get_document_choices("AAPL", 2026, "8k"))

        assert choices == [{"label": "2026-07-24 - 8-K", "value": "https://x/a.pdf"}]

    def test_titles_other_form_groups(self, monkeypatch):
        """A non-8-K group is title-cased in the label."""

        async def _fetch(params, credentials):
            return [_Item(filing_date=date(2026, 1, 1), pdf_url="https://x/b.pdf")]

        monkeypatch.setattr(
            "openbb_nasdaq.models.company_filings.NasdaqCompanyFilingsFetcher.fetch_data",
            _fetch,
        )
        choices = asyncio.run(helpers.get_document_choices("AAPL", 2026, "annual"))

        assert choices[0]["label"].endswith("- Annual")

    def test_failure_yields_no_choices(self, monkeypatch):
        """A symbol with no filings degrades to an empty picker."""

        async def _fetch(params, credentials):
            raise RuntimeError("no filings")

        monkeypatch.setattr(
            "openbb_nasdaq.models.company_filings.NasdaqCompanyFilingsFetcher.fetch_data",
            _fetch,
        )

        assert asyncio.run(helpers.get_document_choices("NOPE", 2026, "8k")) == []


class TestFilingDocuments:
    """Cover the filing download and viewer payload."""

    def test_download_is_base64(self, monkeypatch):
        """The PDF body is read through the callback and base64-encoded."""

        class _Response:
            async def read(self):
                """Return the raw body."""
                return b"%PDF-1.4 body"

        async def _request(url, **kwargs):
            return await kwargs["response_callback"](_Response(), None)

        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.amake_request", _request
        )
        encoded = asyncio.run(helpers.download_filing_pdf("https://x/a.pdf"))

        assert encoded == "JVBERi0xLjQgYm9keQ=="

    def test_open_returns_the_viewer_payload(self, monkeypatch):
        """A successful download carries the data format and filename."""

        async def _download(url):
            return "QUJD"

        monkeypatch.setattr(helpers, "download_filing_pdf", _download)
        payload = asyncio.run(
            helpers.open_filing_document(
                "https://x/a.pdf?symbol=AAPL&formType=8-K&dateFiled=2026-07-24T00:00:00"
            )
        )

        assert payload["content"] == "QUJD"
        assert payload["data_format"] == {
            "data_type": "pdf",
            "filename": "AAPL-20260724-8K.pdf",
        }

    def test_open_reports_a_failure(self, monkeypatch):
        """A failed download is surfaced as an error payload."""

        async def _download(url):
            raise RuntimeError("404")

        monkeypatch.setattr(helpers, "download_filing_pdf", _download)
        payload = asyncio.run(helpers.open_filing_document("https://x/a.pdf"))

        assert payload["error_type"] == "download_error"
        assert "404" in payload["content"]

    @pytest.mark.parametrize(
        ("url", "expected"),
        [
            (
                "https://x/a.pdf?symbol=MSFT&formType=10-K&dateFiled=2026-01-05T00:00:00",
                "MSFT-20260105-10K.pdf",
            ),
            ("https://x/a.pdf", "filing.pdf"),
            ("https://x/a.pdf?formType=8-K", "filing.pdf"),
        ],
    )
    def test_filename(self, url, expected):
        """A readable filename is built, with a fallback when unidentifiable."""
        assert helpers._filing_filename(url) == expected


class TestContractDetail:
    """Cover the per-strike contract detail."""

    @staticmethod
    def _payload():
        """Return a two-sided contract payload."""
        return {
            "optionChainCallData": {
                "optionChainListData": {
                    "LastSale": {"value": "1.50"},
                    "Market": {"value": "NASDAQ"},
                    "Tick": {"value": "up"},
                },
                "optionChainGreeksList": {"Delta": {"value": "0.55"}},
            },
            "optionChainPutData": {"optionChainListData": {}},
        }

    def test_reads_both_sides(self, monkeypatch):
        """Sides without detail are skipped and text fields stay text."""

        async def _data(path, **kwargs):
            return self._payload()

        monkeypatch.setattr(helpers, "get_nasdaq_data", _data)
        sides = asyncio.run(
            helpers.get_contract_detail("NVDA", date(2026, 8, 7), 187.5)
        )

        assert set(sides) == {"call"}
        assert sides["call"]["last_trade_price"] == 1.5
        assert sides["call"]["exchange"] == "NASDAQ"
        assert sides["call"]["delta"] == 0.55
        assert sides["call"]["gamma"] is None

    def test_empty_payload(self, monkeypatch):
        """A strike Nasdaq does not publish yields nothing."""

        async def _data(path, **kwargs):
            return None

        monkeypatch.setattr(helpers, "get_nasdaq_data", _data)

        assert (
            asyncio.run(helpers.get_contract_detail("X", date(2026, 8, 7), 1.0)) == {}
        )
