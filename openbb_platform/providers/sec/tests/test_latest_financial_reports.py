"""Unit tests for ``openbb_sec.models.latest_financial_reports``."""

import asyncio
from datetime import date

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_sec.models.latest_financial_reports import (
    SecLatestFinancialReportsFetcher,
    SecLatestFinancialReportsQueryParams,
)


def _run(coro):
    """Run an async coroutine from a sync test (no pytest-asyncio)."""
    return asyncio.run(coro)


def _async_return(value):
    """Build a zero-arg awaitable returning ``value``."""

    async def _inner(*args, **kwargs):
        return value

    return _inner


class TestLatestFinancialReportsQuery:
    """report_type validator."""

    def test_valid_report_type(self):
        qp = SecLatestFinancialReportsQueryParams(report_type="10-K")
        assert qp.report_type == "10-K"

    def test_none_report_type(self):
        assert (
            SecLatestFinancialReportsQueryParams(report_type=None).report_type is None
        )

    def test_invalid_report_type_raises(self):
        with pytest.raises(ValueError, match="Invalid report type"):
            SecLatestFinancialReportsQueryParams(report_type="BOGUS")

    def test_transform_query_passthrough(self):
        qp = SecLatestFinancialReportsFetcher.transform_query({})
        assert isinstance(qp, SecLatestFinancialReportsQueryParams)


class TestLatestFinancialReportsTransform:
    """parse_entry coverage via transform_data."""

    def test_parses_and_deduplicates(self):
        entries = [
            {
                "_id": "0000320193-24-000081:aapl-20240630.htm",
                "_source": {
                    "ciks": ["0000320193"],
                    "display_names": ["Apple Inc. (AAPL)"],
                    "sics": ["3571"],
                    "file_date": "2024-08-01",
                    "period_ending": "2024-06-30",
                    "form": "10-K",
                    "file_description": "FORM 10-K",
                    "adsh": "0000320193-24-000081",
                    "items": ["2.02", "9.01"],
                },
            },
            # Duplicate URL -> deduplicated away
            {
                "_id": "0000320193-24-000081:aapl-20240630.htm",
                "_source": {
                    "ciks": ["0000320193"],
                    "display_names": ["Apple Inc. (AAPL)"],
                    "sics": ["3571"],
                    "file_date": "2024-08-01",
                    "period_ending": "2024-06-30",
                    "form": "10-K",
                    "file_description": "FORM 10-K",
                    "adsh": "0000320193-24-000081",
                    "items": ["2.02"],
                },
            },
        ]
        res = SecLatestFinancialReportsFetcher.transform_data(
            SecLatestFinancialReportsQueryParams(), entries
        )
        assert len(res) == 1
        row = res[0]
        assert row.symbol == "AAPL"
        assert row.name == "Apple Inc."
        assert row.cik == "0000320193"
        assert row.sic == "3571"
        assert row.items == "2.02,9.01"
        # 10-K gets MetaLinks + Financial_Report URLs
        assert row.metadata.endswith("MetaLinks.json")
        assert row.financial_report.endswith("Financial_Report.xlsx")
        assert row.index_headers.endswith("-index-headers.html")
        assert row.complete_submission.endswith(".txt")

    def test_8k_metadata_and_ncsr_financial_report(self):
        entries = [
            {
                "_id": "0000320193-24-000099:aapl-8k.htm",
                "_source": {
                    "ciks": ["0000320193"],
                    "display_names": ["Apple Inc. (AAPL)"],
                    "sics": [],
                    "file_date": "2024-08-02",
                    "form": "8-K",
                    "file_description": "FORM 8-K",
                    "adsh": "0000320193-24-000099",
                },
            },
            {
                "_id": "0000320193-24-000100:ncsr.htm",
                "_source": {
                    "ciks": ["0000320193"],
                    "display_names": ["Apple Inc. (AAPL)"],
                    "sics": [],
                    "file_date": "2024-08-03",
                    "form": "N-CSR",
                    "file_description": "FORM N-CSR",
                    "adsh": "0000320193-24-000100",
                },
            },
        ]
        res = SecLatestFinancialReportsFetcher.transform_data(
            SecLatestFinancialReportsQueryParams(), entries
        )
        by_form = {r.report_type: r for r in res}
        # 8-K: both metadata and financial_report present, no items
        assert by_form["8-K"].metadata.endswith("MetaLinks.json")
        assert by_form["8-K"].financial_report.endswith("Financial_Report.xlsx")
        assert by_form["8-K"].items is None
        # N-CSR: financial_report present, but metadata None (not 10-/8-)
        assert by_form["N-CSR"].metadata is None
        assert by_form["N-CSR"].financial_report.endswith("Financial_Report.xlsx")


class TestLatestFinancialReportsExtract:
    """aextract_data branches with patched amake_request."""

    def test_pagination_collects_all_hits(self, monkeypatch):
        state = {"n": 0}

        async def fake_amake(url, **kwargs):
            state["n"] += 1
            if state["n"] == 1:
                return {
                    "hits": {
                        "total": {"value": 3},
                        "hits": [{"_id": "a:1"}, {"_id": "b:2"}],
                    }
                }
            return {"hits": {"total": {"value": 3}, "hits": [{"_id": "c:3"}]}}

        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.amake_request", fake_amake
        )
        q = SecLatestFinancialReportsQueryParams(
            date=date(2024, 11, 5), report_type="10-K"
        )
        out = _run(SecLatestFinancialReportsFetcher.aextract_data(q, None))
        assert len(out) == 3
        assert state["n"] == 2

    def test_non_dict_response_raises(self, monkeypatch):
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.amake_request",
            _async_return(["not", "a", "dict"]),
        )
        q = SecLatestFinancialReportsQueryParams(date=date(2024, 11, 5))
        with pytest.raises(OpenBBError, match="Unexpected data response"):
            _run(SecLatestFinancialReportsFetcher.aextract_data(q, None))

    def test_first_request_error_wrapped(self, monkeypatch):
        async def boom(url, **kwargs):
            raise OpenBBError("boom")

        monkeypatch.setattr("openbb_core.provider.utils.helpers.amake_request", boom)
        q = SecLatestFinancialReportsQueryParams(date=date(2024, 11, 5))
        with pytest.raises(OpenBBError, match="Failed to get SEC data"):
            _run(SecLatestFinancialReportsFetcher.aextract_data(q, None))

    def test_empty_results_branches(self, monkeypatch):
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.amake_request",
            _async_return({"hits": {"total": {"value": 0}, "hits": []}}),
        )
        # report_type set -> EmptyDataError
        q1 = SecLatestFinancialReportsQueryParams(
            date=date(2024, 11, 5), report_type="10-K"
        )
        with pytest.raises(EmptyDataError):
            _run(SecLatestFinancialReportsFetcher.aextract_data(q1, None))
        # report_type None -> OpenBBError "No data was returned."
        q2 = SecLatestFinancialReportsQueryParams(date=date(2024, 11, 5))
        with pytest.raises(OpenBBError, match="No data was returned"):
            _run(SecLatestFinancialReportsFetcher.aextract_data(q2, None))

    def test_pagination_break_on_error_warns(self, monkeypatch):
        state = {"n": 0}

        async def fake_amake(url, **kwargs):
            state["n"] += 1
            if state["n"] == 1:
                return {"hits": {"total": {"value": 5}, "hits": [{"_id": "a:1"}]}}
            raise RuntimeError("net down")

        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.amake_request", fake_amake
        )
        q = SecLatestFinancialReportsQueryParams(date=date(2024, 11, 5))
        with pytest.warns(Warning, match="Failed to get the next page"):
            out = _run(SecLatestFinancialReportsFetcher.aextract_data(q, None))
        assert len(out) == 1

    def test_weekend_date_rolled_back_to_friday(self, monkeypatch):
        captured = {}

        async def fake_amake(url, **kwargs):
            captured.setdefault("url", url)
            return {"hits": {"total": {"value": 1}, "hits": [{"_id": "a:1"}]}}

        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.amake_request", fake_amake
        )
        # 2024-11-09 is a Saturday -> rolled back to Friday 2024-11-08.
        q = SecLatestFinancialReportsQueryParams(date=date(2024, 11, 9))
        _run(SecLatestFinancialReportsFetcher.aextract_data(q, None))
        assert "startdt=2024-11-08" in captured["url"]

    def test_pagination_break_on_empty_next_page(self, monkeypatch):
        state = {"n": 0}

        async def fake_amake(url, **kwargs):
            state["n"] += 1
            if state["n"] == 1:
                return {"hits": {"total": {"value": 5}, "hits": [{"_id": "a:1"}]}}
            # Next page returns no hits -> loop breaks.
            return {"hits": {"total": {"value": 5}, "hits": []}}

        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.amake_request", fake_amake
        )
        q = SecLatestFinancialReportsQueryParams(date=date(2024, 11, 5))
        out = _run(SecLatestFinancialReportsFetcher.aextract_data(q, None))
        assert len(out) == 1
        assert state["n"] == 2
