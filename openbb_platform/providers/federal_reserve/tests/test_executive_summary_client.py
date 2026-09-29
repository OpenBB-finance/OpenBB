"""Tests for the FFIEC Executive Summary Report (ESR) router client."""

from openbb_federal_reserve.utils import executive_summary_report


class TestValue:
    """Tests for the ESR period-cell number parser."""

    def test_blank_cell_is_none(self):
        """An empty cell parses to ``None``."""
        assert executive_summary_report._value("") is None
        assert executive_summary_report._value(None) is None

    def test_numeric_cell_parsed(self):
        """A numeric cell parses to a float."""
        assert executive_summary_report._value("13105") == 13105.0

    def test_non_numeric_cell_is_none(self):
        """A non-numeric cell maps to ``None`` rather than raising."""
        assert executive_summary_report._value("--") is None


class TestReportSections:
    """Tests for the ESR section table-of-contents fetch."""

    def test_filters_to_dict_rows_with_sectionid(self, monkeypatch):
        """Only dict rows carrying a ``sectionid`` survive the producer filter."""
        from openbb_federal_reserve.utils import cache

        monkeypatch.setattr(cache, "cached", lambda _key, _ttl, producer: producer())
        monkeypatch.setattr(
            executive_summary_report,
            "_post",
            lambda requestor_id, criteria: [
                {"sectionid": "SectionA", "displayorder": "1"},
                {"displayorder": "2"},
                "not-a-dict",
            ],
        )
        sections = executive_summary_report.report_sections()
        assert sections == [{"sectionid": "SectionA", "displayorder": "1"}]


class TestNoSections:
    """Tests for the empty table-of-contents short circuit."""

    def test_returns_empty_when_no_sections(self, monkeypatch):
        """An empty section list returns no rows without any further fetch."""
        monkeypatch.setattr(executive_summary_report, "report_sections", lambda: [])
        assert executive_summary_report.fetch_executive_summary("852218") == []


class TestFetchExecutiveSummary:
    """Tests for ``fetch_executive_summary`` guide enrichment and scaling."""

    _SECTIONS = [{"sectionid": "SectionA", "displayorder": "1"}]
    _CYCLES = [{"enddateformatted": "03/31/2026"}]
    _LINES = [
        {
            "displayorder": "1",
            "linecaption": "#SectionTitle#Income Statement $:",
            "conceptname": "",
        },
        {
            "displayorder": "2",
            "linecaption": "Pretax Net Operating Inc",
            "conceptname": "UBPR1234",
            "lineid": "868900",
            "03_31_2026": "13105",
        },
    ]

    def _patch(self, monkeypatch, guide):
        """Wire every external seam to in-memory fixtures."""
        from openbb_federal_reserve.utils import cache, concepts

        monkeypatch.setattr(
            executive_summary_report,
            "report_sections",
            lambda: list(self._SECTIONS),
        )
        monkeypatch.setattr(
            executive_summary_report,
            "report_cycles",
            lambda: list(self._CYCLES),
        )
        monkeypatch.setattr(
            executive_summary_report,
            "_post",
            lambda requestor_id, criteria: list(self._LINES),
        )
        monkeypatch.setattr(cache, "cached", lambda _key, _ttl, producer: producer())
        monkeypatch.setattr(
            concepts,
            "concept_index",
            lambda _product, _form: {
                "UBPR1234": {
                    "name": "Pretax Net Operating Inc",
                    "monetary": True,
                    "narrative": None,
                }
            },
        )
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.guide.fetch_guide_concepts",
            lambda _concepts, lines=None: guide,
        )

    def test_label_from_guide_description_and_narrative(self, monkeypatch):
        """A line item takes the cleaned guide Description and the guide Narrative."""
        self._patch(
            monkeypatch,
            {
                "UBPR1234": {
                    "description": (
                        "Pretax Net Operating Income (TE) as a percent of"
                        " Average Assets"
                    ),
                    "narrative": "Pretax net operating income definition.",
                }
            },
        )
        rows = executive_summary_report.fetch_executive_summary("852218")
        line = next(r for r in rows if not r["is_header"])
        assert line["label"] == "Pretax Net Operating Income (TE)"
        assert line["narrative"] == "Pretax net operating income definition."
        assert line["2026-03-31"] == 13105 * 1000

    def test_header_label_untouched_and_narrative_none(self, monkeypatch):
        """A header row keeps its caption label and carries no narrative."""
        self._patch(
            monkeypatch,
            {
                "UBPR1234": {
                    "description": "Pretax Net Operating Income (TE)",
                    "narrative": "Pretax net operating income definition.",
                }
            },
        )
        rows = executive_summary_report.fetch_executive_summary("852218")
        header = next(r for r in rows if r["is_header"])
        assert header["label"] == "Income Statement $:"
        assert header["narrative"] is None

    def test_falls_back_to_mdrm_name_without_guide(self, monkeypatch):
        """A concept absent from the guide falls back to the MDRM name."""
        self._patch(monkeypatch, {})
        rows = executive_summary_report.fetch_executive_summary("852218")
        line = next(r for r in rows if not r["is_header"])
        assert line["label"] == "Pretax Net Operating Inc"
        assert line["narrative"] is None

    def test_blank_line_dropped(self, monkeypatch):
        """A ``#BlankLine#`` row is skipped entirely from the section output."""
        from openbb_federal_reserve.utils import cache, concepts

        lines = [
            {
                "displayorder": "1",
                "linecaption": "#BlankLine#",
                "conceptname": "",
            },
            {
                "displayorder": "2",
                "linecaption": "Pretax Net Operating Inc",
                "conceptname": "UBPR1234",
                "lineid": "868900",
                "03_31_2026": "13105",
            },
        ]
        monkeypatch.setattr(
            executive_summary_report,
            "report_sections",
            lambda: [{"sectionid": "SectionA", "displayorder": "1"}],
        )
        monkeypatch.setattr(
            executive_summary_report,
            "report_cycles",
            lambda: [{"enddateformatted": "03/31/2026"}],
        )
        monkeypatch.setattr(
            executive_summary_report,
            "_post",
            lambda requestor_id, criteria: list(lines),
        )
        monkeypatch.setattr(cache, "cached", lambda _key, _ttl, producer: producer())
        monkeypatch.setattr(
            concepts,
            "concept_index",
            lambda _product, _form: {
                "UBPR1234": {
                    "name": "Pretax Net Operating Inc",
                    "monetary": True,
                    "narrative": None,
                }
            },
        )
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.guide.fetch_guide_concepts",
            lambda _concepts, lines=None: {},
        )
        rows = executive_summary_report.fetch_executive_summary("852218")
        assert all(r["label"] != "#BlankLine#" for r in rows)
        assert any(not r["is_header"] for r in rows)

    def test_call_sourced_line_uses_concept_index_narrative(self, monkeypatch):
        """A Call-sourced (RIAD) line takes the concept-index narrative as fallback.

        The FFIEC guide carries no narrative for Call Report concepts, while a
        plain UBPR concept keeps its guide narrative untouched.
        """
        from openbb_federal_reserve.utils import cache, concepts

        sections = [{"sectionid": "SectionA", "displayorder": "1"}]
        cycles = [{"enddateformatted": "03/31/2026"}]
        lines = [
            {
                "displayorder": "1",
                "linecaption": "Pretax Net Operating Inc",
                "conceptname": "UBPR1234",
                "lineid": "868900",
                "03_31_2026": "13105",
            },
            {
                "displayorder": "2",
                "linecaption": "Lease Financing Income",
                "conceptname": "RIAD4065",
                "lineid": "868901",
                "03_31_2026": "42",
            },
        ]
        monkeypatch.setattr(
            executive_summary_report, "report_sections", lambda: list(sections)
        )
        monkeypatch.setattr(
            executive_summary_report, "report_cycles", lambda: list(cycles)
        )
        monkeypatch.setattr(
            executive_summary_report,
            "_post",
            lambda requestor_id, criteria: list(lines),
        )
        monkeypatch.setattr(cache, "cached", lambda _key, _ttl, producer: producer())
        monkeypatch.setattr(
            concepts,
            "concept_index",
            lambda _product, _form: {
                "UBPR1234": {
                    "name": "Pretax Net Operating Inc",
                    "monetary": True,
                    "narrative": None,
                },
                "RIAD4065": {
                    "name": "Lease Financing Income",
                    "monetary": True,
                    "narrative": (
                        "Includes amortized income from direct and leveraged"
                        " financing leases."
                    ),
                },
            },
        )
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.guide.fetch_guide_concepts",
            lambda _concepts, lines=None: {
                "UBPR1234": {
                    "description": "Pretax Net Operating Income (TE)",
                    "narrative": "Pretax net operating income definition.",
                }
            },
        )
        rows = executive_summary_report.fetch_executive_summary("852218")
        ubpr_line = next(r for r in rows if r["label"].endswith("(TE)"))
        call_line = next(r for r in rows if r["label"] == "Lease Financing Income")
        assert ubpr_line["narrative"] == "Pretax net operating income definition."
        assert call_line["narrative"] == (
            "Includes amortized income from direct and leveraged financing leases."
        )
