"""Tests for the shared report-structure generator helpers."""

from datetime import date

from openbb_federal_reserve.utils import structure_common
from openbb_federal_reserve.utils.structure_common import (
    asset_path,
    collect_schedules,
    fetch_pdf_bytes,
    fetch_report_csv,
    latest_quarter_end,
)


class TestLatestQuarterEnd:
    """Coverage for the validation quarter-end resolver."""

    def test_picks_most_recent_completed(self):
        """The most recent quarter end strictly before the date is chosen."""
        assert latest_quarter_end(date(2025, 5, 15)) == "20250331"

    def test_january_uses_prior_year_end(self):
        """A January date resolves to the prior December quarter end."""
        assert latest_quarter_end(date(2025, 1, 10)) == "20241231"

    def test_defaults_to_today(self, monkeypatch):
        """With no argument the resolver uses the current date."""

        class _Date(date):
            @classmethod
            def today(cls):
                """Freeze today at a mid-Q3 date."""
                return cls(2025, 8, 1)

        monkeypatch.setattr(structure_common, "date", _Date)
        assert latest_quarter_end() == "20250630"


class TestFetchPdfBytes:
    """Coverage for the public PDF downloader."""

    def test_returns_body(self, monkeypatch):
        """The response body is returned after a status check."""
        import requests

        class _Resp:
            content = b"%PDF-1.7 body"

            def raise_for_status(self):
                """No-op success."""

        monkeypatch.setattr(requests, "get", lambda *a, **k: _Resp())
        assert fetch_pdf_bytes("https://example.test/guide.pdf") == b"%PDF-1.7 body"


class TestFetchReportCsv:
    """Coverage for the per-institution CSV fetch."""

    def test_decodes_bytes(self, monkeypatch):
        """The NIC CSV bytes are fetched and decoded to text."""
        import openbb_federal_reserve.utils.ffiec as ffiec_mod

        captured = {}

        def _fetch(path, referer=None):
            """Capture the request path and return CSV bytes."""
            captured["path"] = path
            return b"ItemName,Description,Value\n"

        monkeypatch.setattr(ffiec_mod, "_fetch_bytes", _fetch)
        result = fetch_report_csv("FFIEC002", 317810, "20260331")
        assert result == "ItemName,Description,Value\n"
        assert "rpt=FFIEC002" in captured["path"]
        assert "id=317810" in captured["path"]
        assert "dt=20260331" in captured["path"]


class TestCollectSchedules:
    """Coverage for the distinct-schedule collector."""

    def test_first_seen_order_and_blank_skipped(self):
        """Distinct schedules keep first-seen order and blanks are dropped."""
        items = [
            {"schedule": "RAL", "schedule_name": "Schedule RAL"},
            {"schedule": "RAL", "schedule_name": "Schedule RAL"},
            {"schedule": "", "schedule_name": ""},
            {"schedule": "A", "schedule_name": "Schedule A"},
        ]
        assert collect_schedules(items) == [
            {"schedule": "RAL", "name": "Schedule RAL"},
            {"schedule": "A", "name": "Schedule A"},
        ]


class TestAssetPath:
    """Coverage for the committed-asset path builder."""

    def test_points_at_structure_json(self):
        """The path lands at ``assets/<dir>/structure.json``."""
        path = asset_path("ffiec002")
        assert path.parts[-3:] == ("assets", "ffiec002", "structure.json")
