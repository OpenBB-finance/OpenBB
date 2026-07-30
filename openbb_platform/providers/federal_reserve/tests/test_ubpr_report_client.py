"""Tests for the FFIEC UBPR report-router client (``utils/ubpr_report``)."""

import pytest

from openbb_federal_reserve.utils import ubpr_report


def _bypass_cache(monkeypatch):
    """Run every ``cached`` producer body directly against the fixtures."""
    from openbb_federal_reserve.utils import cache

    monkeypatch.setattr(cache, "cached", lambda _key, _ttl, producer: producer())


class TestReportCycles:
    """Tests for ``report_cycles``."""

    def test_filters_and_sorts_newest_first(self, monkeypatch):
        """Non-cycle rows drop out and the survivors sort by end date, newest first."""
        _bypass_cache(monkeypatch)
        rows = [
            {"reportingcycleid": "1", "enddateformatted": "03/31/2025"},
            {"reportingcycleid": "2", "enddateformatted": "03/31/2026"},
            "not-a-dict",
            {"enddateformatted": "12/31/2025"},
        ]
        monkeypatch.setattr(ubpr_report, "_post", lambda requestor, criteria: rows)
        result = ubpr_report.report_cycles()
        assert [r["reportingcycleid"] for r in result] == ["2", "1"]


class TestReportSections:
    """Tests for ``report_sections``."""

    def test_keeps_only_rows_with_pageid(self, monkeypatch):
        """Rows without a ``pageid`` (and non-dicts) are dropped from the list."""
        _bypass_cache(monkeypatch)
        rows = [
            {"pageid": "p1", "pagetitle": "Summary Ratios"},
            {"pagetitle": "No Page Id"},
            "not-a-dict",
        ]
        captured: dict = {}

        def _post(requestor, criteria):
            """Capture the criteria the producer sends to the router."""
            captured.update(criteria)
            return rows

        monkeypatch.setattr(ubpr_report, "_post", _post)
        result = ubpr_report.report_sections(283)
        assert result == [{"pageid": "p1", "pagetitle": "Summary Ratios"}]
        assert captured == {"ReportTypeID": 283}


class TestSectionId:
    """Tests for ``_section_id``."""

    _SECTIONS = [
        {"pageid": "p1", "pagetitle": "Summary Ratios"},
        {"pageid": "p2", "pagetitle": "Income Statement $"},
    ]

    def test_empty_section_list_raises(self, monkeypatch):
        """An empty section list raises ``ValueError``."""
        monkeypatch.setattr(ubpr_report, "report_sections", lambda report_type_id: [])
        with pytest.raises(ValueError, match="could not be retrieved"):
            ubpr_report._section_id("Summary Ratios", 283)

    def test_blank_section_returns_first(self, monkeypatch):
        """A blank section resolves to the first available page."""
        monkeypatch.setattr(
            ubpr_report, "report_sections", lambda report_type_id: list(self._SECTIONS)
        )
        assert ubpr_report._section_id(None, 283) == ("p1", "Summary Ratios")

    def test_match_by_pageid(self, monkeypatch):
        """A pageid string resolves to its ``(pageid, title)``."""
        monkeypatch.setattr(
            ubpr_report, "report_sections", lambda report_type_id: list(self._SECTIONS)
        )
        assert ubpr_report._section_id("p2", 283) == ("p2", "Income Statement $")

    def test_match_by_title_case_insensitive(self, monkeypatch):
        """A title resolves case-insensitively to its ``(pageid, title)``."""
        monkeypatch.setattr(
            ubpr_report, "report_sections", lambda report_type_id: list(self._SECTIONS)
        )
        assert ubpr_report._section_id("summary ratios", 283) == (
            "p1",
            "Summary Ratios",
        )

    def test_unknown_section_raises(self, monkeypatch):
        """An unknown section title raises ``ValueError``."""
        monkeypatch.setattr(
            ubpr_report, "report_sections", lambda report_type_id: list(self._SECTIONS)
        )
        with pytest.raises(ValueError, match="Unknown report section"):
            ubpr_report._section_id("Nope", 283)


class TestNoBankReportError:
    """Tests for ``no_bank_report_error``."""

    def test_message_is_actionable(self):
        """The error names the RSSD, the report, and the FR Y-9C alternative."""
        from openbb_core.app.model.abstract.error import OpenBBError

        error = ubpr_report.no_bank_report_error("2162966", "UBPR")
        assert isinstance(error, OpenBBError)
        message = str(error)
        assert "No UBPR data for RSSD 2162966" in message
        assert "FFIEC Call Report" in message
        assert "subsidiary bank's RSSD" in message
        assert "financial_statements" in message


class TestNumber:
    """Tests for ``_number``."""

    def test_whole_value_returns_int(self):
        """A whole numeric string parses to an ``int``."""
        assert ubpr_report._number("12") == 12
        assert isinstance(ubpr_report._number("12"), int)

    def test_fractional_value_returns_float(self):
        """A fractional value parses to a ``float``."""
        assert ubpr_report._number("12.5") == 12.5

    def test_non_numeric_returns_none(self):
        """A non-numeric value returns ``None``."""
        assert ubpr_report._number("n/a") is None
        assert ubpr_report._number(None) is None


class TestFetchListOfBanks:
    """Tests for ``fetch_list_of_banks``."""

    def test_normalizes_records(self, monkeypatch):
        """Each roster record maps source fields, trims strings, and coerces numbers."""
        _bypass_cache(monkeypatch)
        raw = [
            {
                "rssd9001": " 451965 ",
                "rssd9050": "3511",
                "ubpr9346": "N",
                "rssd9017": " Wells Fargo ",
                "rssd9130": "Sioux Falls",
                "rssd9200": "SD",
                "statename": "South Dakota",
                "ubprd218": "10",
                "ubprd659": "1234567.0",
                "ubpr4340": "1500.5",
                "latitude": "43.5",
                "longitude": "-96.7",
            }
        ]
        captured: dict = {}

        def _post(requestor, criteria):
            """Capture the criteria and return the canned roster."""
            captured.update(criteria)
            return raw

        monkeypatch.setattr(ubpr_report, "_post", _post)
        result = ubpr_report.fetch_list_of_banks("PG1", "1")
        assert captured == {
            "ReportingCycleID": "1",
            "PeerGroupName": "PG1",
            "MaxRows": 0,
        }
        row = result[0]
        assert row["rssd_id"] == "451965"
        assert row["name"] == "Wells Fargo"
        assert row["offices"] == 10
        assert isinstance(row["offices"], int)
        assert row["average_assets"] == 1234567
        assert row["net_income"] == 1500.5
        assert row["latitude"] == 43.5
        assert row["longitude"] == -96.7

    def test_non_list_response_yields_empty(self, monkeypatch):
        """A non-list router response produces an empty roster."""
        _bypass_cache(monkeypatch)
        monkeypatch.setattr(ubpr_report, "_post", lambda requestor, criteria: {})
        assert ubpr_report.fetch_list_of_banks("PG1", "1") == []


class _Session:
    """A canned session returning the ``MyUbprLinesData`` section grid."""

    def __init__(self, rows):
        """Store the line rows the router POST resolves to."""
        self._rows = rows

    def post(self, url, data=None, headers=None, timeout=None):
        """Return the section's line rows as the router response."""
        rows = self._rows
        return type("R", (), {"json": lambda self: rows})()


class TestFetchUbprSectionBranches:
    """Tests for ``fetch_ubpr_section`` branches not covered by the model tests."""

    def _wire(self, monkeypatch, rows, *, concepts, guide, title="Summary Ratios"):
        """Point the client at canned cycles, section, session, concepts, and guide."""
        cycles = [{"reportingcycleid": "1", "enddateformatted": "3/31/2026"}]
        monkeypatch.setattr(ubpr_report, "report_cycles", lambda: cycles)
        monkeypatch.setattr(
            ubpr_report,
            "_section_id",
            lambda section, report_type_id: ("p1", title),
        )
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.cache.cached",
            lambda key, ttl, producer: producer(),
        )
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.cdr._get_session",
            lambda: _Session(rows),
        )
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.concepts.concept_index",
            lambda name: concepts,
        )
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.guide.fetch_guide_concepts",
            lambda concepts, lines=None: guide,
        )

    def test_empty_raw_returns_empty_rows(self, monkeypatch):
        """An empty router response returns the section title with no rows."""
        self._wire(monkeypatch, [], concepts={}, guide={})
        result = ubpr_report.fetch_ubpr_section("852218", "Summary Ratios")
        assert result == {"section": "Summary Ratios", "rows": []}

    def test_blank_line_caption_is_skipped(self, monkeypatch):
        """A ``#BlankLine#`` caption row is dropped from the output rows."""
        rows = [
            {
                "linedisplayorder": "1",
                "linecaption": "#SectionTitle#Earnings",
                "lineid": "100",
                "03_31_2026": None,
            },
            {
                "linedisplayorder": "2",
                "linecaption": "#BlankLine#",
                "lineid": "101",
                "03_31_2026": None,
            },
            {
                "linedisplayorder": "3",
                "linecaption": "Net Inc",
                "lineid": "102",
                "03_31_2026": "1.31;UBPR4340, 1.11;UBPS4340, 80.0;UBPK4340",
            },
        ]
        self._wire(
            monkeypatch,
            rows,
            concepts={
                "UBPR4340": {"monetary": False, "name": "Net Inc"},
                "UBPS4340": {"monetary": False, "name": "Net Inc"},
            },
            guide={
                "UBPR4340": {"description": "Net Income", "narrative": "Net income."}
            },
        )
        result = ubpr_report.fetch_ubpr_section("852218", "Summary Ratios")
        assert all(r["label"] != "#BlankLine#" for r in result["rows"])
        assert sum(not r["is_header"] for r in result["rows"]) == 1

    def test_ratio_page_scales_monetary_peer_group(self, monkeypatch):
        """A monetary peer-group part scales by a thousand on a ratio (PG/PCT) page."""
        rows = [
            {
                "linedisplayorder": "1",
                "linecaption": "#SectionTitle#Balances",
                "lineid": "100",
                "03_31_2026": None,
            },
            {
                "linedisplayorder": "2",
                "linecaption": "Total Assets",
                "lineid": "101",
                "03_31_2026": "100.0;UBPR2170, 200.0;UBPS2170, 55.0;UBPK2170",
            },
        ]
        self._wire(
            monkeypatch,
            rows,
            concepts={
                "UBPR2170": {"monetary": True, "name": "Total Assets"},
                "UBPS2170": {"monetary": True, "name": "Total Assets PG"},
            },
            guide={"UBPR2170": {"description": "Total Assets", "narrative": "Assets."}},
            title="Balance Sheet $",
        )
        result = ubpr_report.fetch_ubpr_section("852218", "Balance Sheet $")
        line = next(r for r in result["rows"] if not r["is_header"])
        assert line["2026-03-31 Bank"] == 100.0 * 1000
        assert line["2026-03-31 PG"] == 200.0 * 1000
        assert line["2026-03-31 PCT"] == 55.0

    def test_all_periods_emits_plain_bank_columns(self, monkeypatch):
        """``all_periods`` emits one plain ``<ISO>`` bank column and omits PG/PCT."""
        rows = [
            {
                "linedisplayorder": "1",
                "linecaption": "#SectionTitle#Earnings",
                "lineid": "100",
                "03_31_2026": None,
            },
            {
                "linedisplayorder": "2",
                "linecaption": "Net Inc",
                "lineid": "101",
                "03_31_2026": "1.31;UBPR4340, 1.11;UBPS4340, 80.0;UBPK4340",
            },
        ]
        self._wire(
            monkeypatch,
            rows,
            concepts={
                "UBPR4340": {"monetary": False, "name": "Net Inc"},
                "UBPS4340": {"monetary": False, "name": "Net Inc"},
            },
            guide={
                "UBPR4340": {"description": "Net Income", "narrative": "Net income."}
            },
        )
        result = ubpr_report.fetch_ubpr_section(
            "852218", "Summary Ratios", all_periods=True
        )
        line = next(r for r in result["rows"] if not r["is_header"])
        assert line["2026-03-31"] == 1.31
        assert "2026-03-31 Bank" not in line
        assert "2026-03-31 PG" not in line
