"""Unit tests for ``openbb_sec.models.company_filings``."""

import asyncio
import types
from datetime import date

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_sec.models.company_filings import (
    SecCompanyFilingsData,
    SecCompanyFilingsFetcher,
    SecCompanyFilingsQueryParams,
)


def _run(coro):
    """Run an async coroutine from a sync test (no pytest-asyncio)."""
    return asyncio.run(coro)


def _async_return(value):
    """Build a zero-arg awaitable returning ``value``."""

    async def _inner(*args, **kwargs):
        return value

    return _inner


class TestCompanyFilingsQuery:
    """SecCompanyFilingsQueryParams.validate_form_type branches."""

    def test_single_string_form(self):
        assert SecCompanyFilingsQueryParams(form_type="10-K").form_type == "10-K"

    def test_lowercase_is_upcased(self):
        assert SecCompanyFilingsQueryParams(form_type="10-k").form_type == "10-K"

    def test_list_of_forms_joined(self):
        qp = SecCompanyFilingsQueryParams(form_type=["10-K", "8-K"])
        assert qp.form_type == "10-K,8-K"

    def test_empty_form_returns_none(self):
        assert SecCompanyFilingsQueryParams(form_type="").form_type is None

    def test_catalog_and_live_codes_kept(self):
        qp = SecCompanyFilingsQueryParams(form_type="10-K,BOGUS")
        assert qp.form_type == "10-K,BOGUS"

    def test_live_code_accepted(self):
        assert SecCompanyFilingsQueryParams(form_type="BOGUS").form_type == "BOGUS"

    def test_unexpected_type_raises(self):
        with pytest.raises(OpenBBError, match="Unexpected form_type value"):
            SecCompanyFilingsQueryParams.validate_form_type(123)

    def test_transform_query_passthrough(self):
        qp = SecCompanyFilingsFetcher.transform_query({"symbol": "AAPL"})
        assert isinstance(qp, SecCompanyFilingsQueryParams)
        assert qp.symbol == "AAPL"


class TestCompanyFilingsDataValidator:
    """SecCompanyFilingsData.validate_report_date branches."""

    def test_string_date_parsed(self):
        d = SecCompanyFilingsData.validate_report_date("2024-06-30")
        assert d == date(2024, 6, 30)

    def test_passthrough_date(self):
        assert SecCompanyFilingsData.validate_report_date(date(2024, 1, 1)) == date(
            2024, 1, 1
        )

    def test_empty_string_is_none(self):
        assert SecCompanyFilingsData.validate_report_date("") is None

    def test_none_is_none(self):
        assert SecCompanyFilingsData.validate_report_date(None) is None


def _filing_records():
    return [
        {
            "reportDate": "2024-06-30",
            "filingDate": "2024-08-01",
            "acceptanceDateTime": "2024-08-01T10:00:00",
            "act": "34",
            "form": "10-K",
            "items": "",
            "primaryDocDescription": "10-K",
            "primaryDocument": "aapl.htm",
            "accessionNumber": "0000320193-24-000081",
            "fileNumber": "001-1",
            "filmNumber": "1",
            "isInlineXBRL": "1",
            "isXBRL": "1",
            "size": "1000",
        },
        {
            "reportDate": "2023-06-30",
            "filingDate": "2023-08-01",
            "acceptanceDateTime": "2023-08-01T10:00:00",
            "act": "34",
            "form": "8-K",
            "items": "",
            "primaryDocDescription": "8-K",
            "primaryDocument": "aapl8k.htm",
            "accessionNumber": "0000320193-23-000077",
            "fileNumber": "001-1",
            "filmNumber": "2",
            "isInlineXBRL": "1",
            "isXBRL": "1",
            "size": "900",
        },
    ]


class TestCompanyFilingsTransformData:
    """SecCompanyFilingsFetcher.transform_data branches."""

    def test_filters_by_date_form_and_limit(self):
        q = types.SimpleNamespace(
            cik="0000320193",
            symbol="AAPL",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 12, 31),
            form_type="10-K",
            limit=5,
        )
        res = SecCompanyFilingsFetcher.transform_data(q, _filing_records())
        assert len(res) == 1
        row = res[0]
        assert isinstance(row, SecCompanyFilingsData)
        assert row.report_type == "10-K"
        # URLs assembled from accession number + primary document
        assert row.report_url.endswith("/000032019324000081/aapl.htm")
        assert row.complete_submission_url.endswith("/0000320193-24-000081.txt")
        assert row.filing_detail_url.endswith("-index.htm")

    def test_empty_data_raises(self):
        q = types.SimpleNamespace(
            cik="0000320193",
            symbol=None,
            start_date=None,
            end_date=None,
            form_type=None,
            limit=None,
        )
        with pytest.raises(EmptyDataError):
            SecCompanyFilingsFetcher.transform_data(q, [])

    def test_filters_remove_all_raises(self):
        q = types.SimpleNamespace(
            cik="0000320193",
            symbol=None,
            start_date=date(2030, 1, 1),
            end_date=None,
            form_type=None,
            limit=None,
        )
        with pytest.raises(EmptyDataError, match="No filings were found"):
            SecCompanyFilingsFetcher.transform_data(q, _filing_records())

    def test_underscore_form_type_and_limit_zero(self):
        # limit == 0 keeps everything; underscore in form_type becomes a space
        q = types.SimpleNamespace(
            cik="320193",
            symbol=None,
            start_date=None,
            end_date=date(2025, 1, 1),
            form_type="10-K",
            limit=0,
        )
        res = SecCompanyFilingsFetcher.transform_data(q, _filing_records())
        assert len(res) == 1


class TestCompanyFilingsExtract:
    """SecCompanyFilingsFetcher.aextract_data branches."""

    def test_no_cik_or_symbol_raises(self):
        q = SecCompanyFilingsQueryParams(symbol=None, cik=None)
        with pytest.raises(OpenBBError, match="CIK or symbol must be provided"):
            _run(SecCompanyFilingsFetcher.aextract_data(q, None))

    def test_symbol_without_cik_raises(self, monkeypatch):
        q = SecCompanyFilingsQueryParams(symbol="ZZZZ", cik=None, use_cache=False)
        monkeypatch.setattr("openbb_sec.utils.helpers.symbol_map", _async_return(""))
        with pytest.raises(OpenBBError, match="CIK not found for symbol"):
            _run(SecCompanyFilingsFetcher.aextract_data(q, None))

    def test_cik_padded_to_ten_digits(self, monkeypatch):
        q = SecCompanyFilingsQueryParams(cik="320193", use_cache=False)
        payload = {
            "filings": {
                "recent": {
                    "form": ["10-K"],
                    "accessionNumber": ["0000320193-24-000081"],
                    "filingDate": ["2024-08-01"],
                },
                "files": [],
            }
        }
        seen = {}

        async def fake_cached_request(url, **kwargs):
            seen["url"] = url
            return payload

        monkeypatch.setattr(
            "openbb_sec.utils.cache.cached_request", fake_cached_request
        )
        out = _run(SecCompanyFilingsFetcher.aextract_data(q, None))
        assert q.cik == "0000320193"
        assert seen["url"] == "https://data.sec.gov/submissions/CIK0000320193.json"
        assert len(out) == 1

    def test_custom_pagination_with_files(self, monkeypatch):
        # form_type set -> follow the additional "files" pages
        q = SecCompanyFilingsQueryParams(
            cik="0000320193", form_type="10-K", use_cache=False
        )
        main = {
            "filings": {
                "recent": {
                    "form": ["10-K"],
                    "accessionNumber": ["0000320193-24-000081"],
                    "filingDate": ["2024-08-01"],
                },
                "files": [{"name": "CIK0000320193-submissions-001.json"}],
            }
        }
        extra = [
            {
                "form": ["10-Q"],
                "accessionNumber": ["0000320193-23-000077"],
                "filingDate": ["2023-05-01"],
            }
        ]

        async def fake_cached_request(url, **kwargs):
            if url.endswith("-001.json"):
                return extra
            return main

        monkeypatch.setattr(
            "openbb_sec.utils.cache.cached_request", fake_cached_request
        )
        out = _run(SecCompanyFilingsFetcher.aextract_data(q, None))
        assert len(out) == 2
