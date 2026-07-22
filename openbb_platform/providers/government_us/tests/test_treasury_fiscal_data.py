"""Tests for the FiscalData API client."""

import asyncio
from datetime import date, timedelta

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_government_us.treasury.utils import fiscal_data


class TestDefaultStartDate:
    """Tests for the trailing-window default start-date helper."""

    def test_explicit_start_is_returned(self):
        """An explicit start date is returned unchanged."""
        start = date(2010, 1, 1)
        assert fiscal_data.default_start_date(start, None, 365) == start

    def test_defaults_to_trailing_window_from_today(self):
        """A missing start defaults to today minus the trailing window."""
        assert fiscal_data.default_start_date(None, None, 30) == (
            date.today() - timedelta(days=30)
        )

    def test_window_anchors_on_end_date(self):
        """A missing start anchors the trailing window on the end date."""
        end = date(2020, 6, 30)
        assert fiscal_data.default_start_date(None, end, 365) == (
            end - timedelta(days=365)
        )


def _patch_request(monkeypatch, respond):
    """Patch amake_request with a URL-driven stub; return the recorded URLs."""
    calls: list[str] = []

    async def _fake(url, **kwargs):
        calls.append(url)
        result = respond(url)
        if isinstance(result, Exception):
            raise result
        return result

    monkeypatch.setattr("openbb_core.provider.utils.helpers.amake_request", _fake)
    return calls


def _instant_sleep(monkeypatch):
    """Replace asyncio.sleep so retry backoff completes instantly."""

    async def _sleep(_seconds):
        return None

    monkeypatch.setattr(asyncio, "sleep", _sleep)


class TestBuildFilters:
    """Tests for build_filters."""

    def test_none_values_are_skipped(self):
        """Conditions with a None value are dropped from the filter string."""
        result = fiscal_data.build_filters(
            [
                ("record_date", "gte", "2024-01-01"),
                ("record_date", "lte", None),
            ]
        )
        assert result == "record_date:gte:2024-01-01"

    def test_empty_conditions_return_none(self):
        """An empty condition list yields None."""
        assert fiscal_data.build_filters([]) is None

    def test_all_none_values_return_none(self):
        """A list where every condition value is None yields None."""
        conditions = [("a", "eq", None), ("b", "in", None)]
        assert fiscal_data.build_filters(conditions) is None

    def test_multiple_conditions_are_comma_joined(self):
        """Multiple applicable conditions join with commas in order."""
        result = fiscal_data.build_filters(
            [
                ("record_date", "gte", "2024-01-01"),
                ("record_date", "lte", "2024-12-31"),
                ("cusip", "in", "(A1,B2)"),
            ]
        )
        assert result == (
            "record_date:gte:2024-01-01,record_date:lte:2024-12-31,cusip:in:(A1,B2)"
        )


class TestGetFiscalData:
    """Tests for get_fiscal_data."""

    def test_single_page(self, monkeypatch):
        """A single-page response returns its rows from one request."""
        calls = _patch_request(
            monkeypatch,
            lambda url: {"data": [{"a": "1"}], "meta": {"total-pages": 1}},
        )
        rows = asyncio.run(fiscal_data.get_fiscal_data("v1/test"))
        assert rows == [{"a": "1"}]
        assert len(calls) == 1
        assert calls[0].startswith(f"{fiscal_data.BASE_URL}v1/test?")
        assert "page[size]=10000" in calls[0]
        assert "page[number]=1" in calls[0]
        assert "filter=" not in calls[0]
        assert "sort=" not in calls[0]

    def test_filters_sort_and_page_size_in_url(self, monkeypatch):
        """Filters, sort, and page_size are encoded as query parameters."""
        calls = _patch_request(
            monkeypatch,
            lambda url: {"data": [{"a": "1"}], "meta": {"total-pages": 1}},
        )
        asyncio.run(
            fiscal_data.get_fiscal_data(
                "v1/test",
                filters="record_date:gte:2024-01-01",
                sort="-record_date",
                page_size=500,
            )
        )
        assert "page[size]=500" in calls[0]
        assert "filter=record_date:gte:2024-01-01" in calls[0]
        assert "sort=-record_date" in calls[0]

    def test_multiple_pages_are_concatenated(self, monkeypatch):
        """Every page reported by the meta total-pages count is fetched."""

        def _respond(url):
            if "page[number]=1" in url:
                return {"data": [{"row": "1"}], "meta": {"total-pages": 2}}
            return {"data": [{"row": "2"}], "meta": {"total-pages": 2}}

        calls = _patch_request(monkeypatch, _respond)
        rows = asyncio.run(fiscal_data.get_fiscal_data("v1/test"))
        assert rows == [{"row": "1"}, {"row": "2"}]
        assert len(calls) == 2
        assert "page[number]=1" in calls[0]
        assert "page[number]=2" in calls[1]

    def test_error_payload_raises_without_retry(self, monkeypatch):
        """An error payload raises OpenBBError immediately."""
        calls = _patch_request(
            monkeypatch,
            lambda url: {"error": "Invalid Query Param", "message": "bad filter"},
        )
        with pytest.raises(OpenBBError, match="Invalid Query Param: bad filter"):
            asyncio.run(fiscal_data.get_fiscal_data("v1/test"))
        assert len(calls) == 1

    def test_garbage_response_retries_then_raises(self, monkeypatch):
        """A non-dict body is retried MAX_RETRIES times and then raises."""
        _instant_sleep(monkeypatch)
        calls = _patch_request(monkeypatch, lambda url: ["not", "a", "dict"])
        with pytest.raises(OpenBBError, match="failed after 3 attempts") as excinfo:
            asyncio.run(fiscal_data.get_fiscal_data("v1/test"))
        assert len(calls) == fiscal_data.MAX_RETRIES
        assert "Unexpected FiscalData response" in str(excinfo.value.__cause__)

    def test_request_exception_retries_then_raises(self, monkeypatch):
        """An amake_request exception is retried and raised as the cause."""
        _instant_sleep(monkeypatch)
        calls = _patch_request(monkeypatch, lambda url: ConnectionError("boom"))
        with pytest.raises(OpenBBError, match="failed after 3 attempts") as excinfo:
            asyncio.run(fiscal_data.get_fiscal_data("v1/test"))
        assert len(calls) == fiscal_data.MAX_RETRIES
        assert isinstance(excinfo.value.__cause__, ConnectionError)

    def test_retry_then_success(self, monkeypatch):
        """A transient failure is retried and the next attempt succeeds."""
        _instant_sleep(monkeypatch)
        state = {"n": 0}

        def _respond(url):
            state["n"] += 1
            if state["n"] == 1:
                return ConnectionError("flaky")
            return {"data": [{"a": "1"}], "meta": {"total-pages": 1}}

        calls = _patch_request(monkeypatch, _respond)
        rows = asyncio.run(fiscal_data.get_fiscal_data("v1/test"))
        assert rows == [{"a": "1"}]
        assert len(calls) == 2

    def test_empty_data_raises(self, monkeypatch):
        """A response with no rows raises EmptyDataError."""
        _patch_request(
            monkeypatch, lambda url: {"data": [], "meta": {"total-pages": 1}}
        )
        with pytest.raises(EmptyDataError):
            asyncio.run(fiscal_data.get_fiscal_data("v1/test"))

    def test_null_and_empty_strings_map_to_none(self, monkeypatch):
        """'null' and empty or whitespace-only strings become None; else pass."""
        _patch_request(
            monkeypatch,
            lambda url: {
                "data": [
                    {
                        "a": "null",
                        "b": "1.5",
                        "c": None,
                        "d": "nullish",
                        "e": "",
                        "f": "   ",
                        "g": "-",
                    }
                ],
                "meta": {"total-pages": 1},
            },
        )
        rows = asyncio.run(fiscal_data.get_fiscal_data("v1/test"))
        assert rows == [
            {
                "a": None,
                "b": "1.5",
                "c": None,
                "d": "nullish",
                "e": None,
                "f": None,
                "g": "-",
            }
        ]
