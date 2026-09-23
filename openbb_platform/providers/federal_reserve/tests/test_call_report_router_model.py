"""Tests for the FFIEC Call Report Sectioned (CDR XBRL bulk) model."""

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_federal_reserve.models.call_report_router import (
    CALL_REPORT_SECTIONS,
    FederalReserveCallReportSectionedData,
    FederalReserveCallReportSectionedFetcher,
    _match,
    _to_number,
)

_HIERARCHY = {
    "RCFD0081": {
        "section": "Schedule RC - Balance Sheet",
        "order": 1,
        "level": 2,
        "label": "Noninterest-bearing balances and currency and coin",
    },
    "RCFD0071": {
        "section": "Schedule RC - Balance Sheet",
        "order": 2,
        "level": 2,
        "label": "Interest-bearing balances",
    },
    "RCFD2170": {
        "section": "Schedule RC - Balance Sheet",
        "order": 3,
        "level": 1,
        "label": "Total assets",
    },
    "RIAD4107": {
        "section": "Schedule RI - Income Statement",
        "order": 1,
        "level": 1,
        "label": "Total interest income",
    },
    "RIAD4461": {
        "section": "Schedule RI-E - Explanations",
        "order": 1,
        "level": 1,
        "label": "Amount of component",
    },
    "TEXT4461": {
        "section": "Schedule RI-E - Explanations",
        "order": 2,
        "level": 1,
        "label": "Describe component",
    },
}

_PARSED = {
    "2026-03-31": {
        "name": "WELLS FARGO BANK, NATIONAL ASSOCIATION",
        "form_type": "031",
        "items": [
            {"mdrm": "RCFD0081", "period": "2026-03-31", "value": "32742000000"},
            {"mdrm": "RCFD0071", "period": "2026-03-31", "value": "140810000000"},
            {"mdrm": "RCFD2170", "period": "2026-03-31", "value": "1900000000000"},
            {"mdrm": "RIAD4107", "period": "2026-03-31", "value": "20000000000"},
        ],
    },
    "2025-12-31": {
        "name": "WELLS FARGO BANK, NATIONAL ASSOCIATION",
        "form_type": "031",
        "items": [
            {"mdrm": "RCFD0081", "period": "2025-12-31", "value": "38677000000"},
            {"mdrm": "RCFD0071", "period": "2025-12-31", "value": "133813000000"},
            {"mdrm": "RCFD2170", "period": "2025-12-31", "value": "1880000000000"},
            {"mdrm": "RIAD4107", "period": "2025-12-31", "value": "82000000000"},
        ],
    },
}

_PARSED_RIE = {
    "2026-03-31": {
        "name": "WELLS FARGO BANK, NATIONAL ASSOCIATION",
        "form_type": "031",
        "items": [
            {"mdrm": "RIAD4461", "period": "2026-03-31", "value": "150000000"},
            {"mdrm": "TEXT4461", "period": "2026-03-31", "value": "CARD FEES"},
        ],
    },
}


_INDEX = {
    "RCFD0081": {
        "name": "Noninterest-Bearing Balances and Currency and Coin",
        "narrative": "Noninterest-bearing balances due from depository institutions.",
        "monetary": True,
        "is_text": False,
    },
    "RCFD0071": {
        "name": "Interest-Bearing Balances",
        "narrative": "Interest-bearing balances due from depository institutions.",
        "monetary": True,
        "is_text": False,
    },
    "RCFD2170": {
        "name": "Total Assets",
        "narrative": "The sum of all asset items on the balance sheet.",
        "monetary": True,
        "is_text": False,
    },
    "RIAD4107": {
        "name": "Total Interest Income",
        "narrative": "The sum of all interest income items.",
        "monetary": True,
        "is_text": False,
    },
    "RIAD4461": {
        "name": "First Itemized Amount That Exceeds 10% Of All Other Noninterest"
        " Income",
        "narrative": "The first component of other noninterest income exceeding"
        " the reporting threshold.",
        "monetary": True,
        "is_text": False,
    },
    "TEXT4461": {
        "name": "First Itemized Amount That Exceeds 10% Of All Other Noninterest"
        " Income",
        "narrative": "The field prefixed by the mnemonic TEXT is the name of the"
        " amount itemized.",
        "monetary": False,
        "is_text": True,
    },
}


def _patch(monkeypatch, parsed=None, filers=None):
    """Point the CDR bulk helpers at in-memory fixtures (no network)."""
    cdr = "openbb_federal_reserve.utils.cdr"
    monkeypatch.setattr(f"{cdr}.fetch_bulk", lambda *a, **k: b"PK\x03\x04rest")
    monkeypatch.setattr(
        f"{cdr}.bulk_rssids",
        lambda content: filers if filers is not None else {"451965"},
    )
    monkeypatch.setattr(
        f"{cdr}.list_periods",
        lambda product: [{"date": d} for d in ("2026-03-31", "2025-12-31")],
    )
    monkeypatch.setattr(
        f"{cdr}.presentation_map", lambda product, form: dict(_HIERARCHY)
    )
    monkeypatch.setattr(
        "openbb_federal_reserve.utils.concepts.concept_index",
        lambda product, form=None: dict(_INDEX),
    )
    store = _PARSED if parsed is None else parsed
    # Each fetch_bulk call returns the latest first, then older periods; resolve
    # the parsed instance by call order to keep the fixture deterministic.
    order = sorted(store, reverse=True)
    state = {"i": 0}

    def _parse(content, rssd):
        """Return the next period's parsed instance in call order."""
        period = order[min(state["i"], len(order) - 1)]
        state["i"] += 1
        return store[period]

    monkeypatch.setattr(f"{cdr}.parse_xbrl_instance", _parse)


class TestToNumber:
    """Tests for the filed-value numeric coercion helper."""

    def test_parses_numeric_string(self):
        """A comma-grouped numeric string coerces to a float."""
        assert _to_number("1,900,000,000,000") == 1900000000000.0

    def test_non_numeric_returns_none(self):
        """A non-numeric token returns ``None`` instead of raising."""
        assert _to_number("NR") is None

    def test_none_returns_none(self):
        """A ``None`` value returns ``None``."""
        assert _to_number(None) is None


class TestMatch:
    """Tests for the schedule-name matcher."""

    def test_normalizes_punctuation(self):
        """Hyphen and spacing differences still match the same schedule."""
        assert _match("Schedule RC - Balance Sheet", "Schedule RC-Balance  Sheet")

    def test_none_candidate(self):
        """A missing candidate never matches."""
        assert _match("Schedule RC - Balance Sheet", None) is False


class TestTransformQuery:
    """Tests for ``transform_query``."""

    def test_requires_identifier(self):
        """Omitting symbol, rssd_id, and fdic_cert raises ``OpenBBError``."""
        with pytest.raises(OpenBBError):
            FederalReserveCallReportSectionedFetcher.transform_query({})

    def test_default_section(self):
        """The section defaults to the balance sheet, a known schedule."""
        query = FederalReserveCallReportSectionedFetcher.transform_query(
            {"rssd_id": "451965"}
        )
        assert query.section == "Schedule RC - Balance Sheet"
        assert query.section in CALL_REPORT_SECTIONS


class TestExtractData:
    """Tests for ``extract_data``."""

    def test_wide_section_rows(self, monkeypatch):
        """The schedule renders as a header plus wide per-period line rows."""
        _patch(monkeypatch)
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ticker.lead_subsidiary_bank",
            lambda rssd, filers, period: "451965",
        )
        query = FederalReserveCallReportSectionedFetcher.transform_query(
            {"rssd_id": "451965"}
        )
        rows = FederalReserveCallReportSectionedFetcher.extract_data(query, None)
        assert rows[0]["is_header"] is True
        assert rows[0]["label"] == "Schedule RC - Balance Sheet"
        line = next(r for r in rows if not r["is_header"])
        assert line["2026-03-31"] == 32742000000.0
        assert line["2025-12-31"] == 38677000000.0
        assert line["label"].endswith(
            "Noninterest-Bearing Balances and Currency and Coin"
        )
        assert (
            line["narrative"]
            == "Noninterest-bearing balances due from depository institutions."
        )
        assert rows[0]["narrative"] is None

    def test_empty_bulk_raises(self, monkeypatch):
        """A non-ZIP bulk response raises ``EmptyDataError``."""
        _patch(monkeypatch)
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.cdr.fetch_bulk", lambda *a, **k: b"<html"
        )
        query = FederalReserveCallReportSectionedFetcher.transform_query(
            {"rssd_id": "451965"}
        )
        with pytest.raises(EmptyDataError):
            FederalReserveCallReportSectionedFetcher.extract_data(query, None)

    def test_unknown_section_raises(self, monkeypatch):
        """A schedule with no matching line items raises ``EmptyDataError``."""
        _patch(monkeypatch)
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ticker.lead_subsidiary_bank",
            lambda rssd, filers, period: "451965",
        )
        query = FederalReserveCallReportSectionedFetcher.transform_query(
            {
                "rssd_id": "451965",
                "section": "Schedule RC-V - Variable Interest Entities",
            }
        )
        with pytest.raises(EmptyDataError):
            FederalReserveCallReportSectionedFetcher.extract_data(query, None)

    def test_no_parsed_facts_raises(self, monkeypatch):
        """A filer whose instances yield no facts raises ``EmptyDataError``."""
        empty = {
            "2026-03-31": {
                "name": "WELLS FARGO BANK, NATIONAL ASSOCIATION",
                "form_type": "",
                "items": [],
            }
        }
        _patch(monkeypatch, parsed=empty)
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.cdr.list_periods",
            lambda product: [{"date": "2026-03-31"}],
        )
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ticker.lead_subsidiary_bank",
            lambda rssd, filers, period: "451965",
        )
        query = FederalReserveCallReportSectionedFetcher.transform_query(
            {"rssd_id": "451965"}
        )
        with pytest.raises(EmptyDataError):
            FederalReserveCallReportSectionedFetcher.extract_data(query, None)

    def test_symbol_resolves_to_bank(self, monkeypatch):
        """A ticker resolves to the filing subsidiary bank's RSSD."""
        _patch(monkeypatch)
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ticker.resolve_ticker_to_bank",
            lambda symbol, filers, period: "451965",
        )
        query = FederalReserveCallReportSectionedFetcher.transform_query(
            {"symbol": "WFC"}
        )
        rows = FederalReserveCallReportSectionedFetcher.extract_data(query, None)
        assert len(rows) > 1

    def test_unresolved_symbol_raises(self, monkeypatch):
        """A ticker that resolves to no filer raises ``OpenBBError``."""
        _patch(monkeypatch)
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ticker.resolve_ticker_to_bank",
            lambda symbol, filers, period: None,
        )
        query = FederalReserveCallReportSectionedFetcher.transform_query(
            {"symbol": "ZZZ"}
        )
        with pytest.raises(OpenBBError):
            FederalReserveCallReportSectionedFetcher.extract_data(query, None)

    def test_all_periods_returns_full_history(self, monkeypatch):
        """``all_periods=True`` returns every period, past the recent-five cap."""
        history = [f"{year}-12-31" for year in range(2025, 2017, -1)]
        parsed = {
            iso: {
                "name": "WELLS FARGO BANK, NATIONAL ASSOCIATION",
                "form_type": "031",
                "items": [
                    {"mdrm": "RCFD0081", "period": iso, "value": "32742000000"},
                ],
            }
            for iso in history
        }

        def _setup():
            """Re-point the helpers for a single extract_data call."""
            _patch(monkeypatch, parsed=parsed)
            monkeypatch.setattr(
                "openbb_federal_reserve.utils.cdr.list_periods",
                lambda product: [{"date": iso} for iso in history],
            )
            monkeypatch.setattr(
                "openbb_federal_reserve.utils.ticker.lead_subsidiary_bank",
                lambda rssd, filers, period: "451965",
            )

        _setup()
        capped = FederalReserveCallReportSectionedFetcher.transform_query(
            {"rssd_id": "451965"}
        )
        capped_rows = FederalReserveCallReportSectionedFetcher.extract_data(
            capped, None
        )
        capped_line = next(r for r in capped_rows if not r["is_header"])
        capped_isos = sorted(k for k in capped_line if k in history)
        assert len(capped_isos) == 5

        _setup()
        full = FederalReserveCallReportSectionedFetcher.transform_query(
            {"rssd_id": "451965", "all_periods": True}
        )
        full_rows = FederalReserveCallReportSectionedFetcher.extract_data(full, None)
        full_line = next(r for r in full_rows if not r["is_header"])
        full_isos = sorted(k for k in full_line if k in history)
        assert len(full_isos) > 5
        assert len(full_isos) == len(history)

    def test_fdic_cert_resolves(self, monkeypatch):
        """An FDIC certificate resolves to the bank's RSSD."""
        _patch(monkeypatch)
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.cdr.resolve_fdic_cert",
            lambda content, cert: "451965",
        )
        query = FederalReserveCallReportSectionedFetcher.transform_query(
            {"fdic_cert": "3511"}
        )
        rows = FederalReserveCallReportSectionedFetcher.extract_data(query, None)
        assert len(rows) > 1

    def test_drops_text_line_items(self, monkeypatch):
        """Free-text ``TEXTxxxx`` concepts are dropped from the numeric grid.

        Only the numeric amount line survives, and it keeps its full name rather
        than the ``% of …`` truncation.
        """
        _patch(monkeypatch, parsed=_PARSED_RIE)
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.cdr.list_periods",
            lambda product: [{"date": "2026-03-31"}],
        )
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ticker.lead_subsidiary_bank",
            lambda rssd, filers, period: "451965",
        )
        query = FederalReserveCallReportSectionedFetcher.transform_query(
            {"rssd_id": "451965", "section": "Schedule RI-E - Explanations"}
        )
        rows = FederalReserveCallReportSectionedFetcher.extract_data(query, None)
        line_rows = [r for r in rows if not r["is_header"]]
        assert len(line_rows) == 1
        line = line_rows[0]
        assert line["2026-03-31"] == 150000000.0
        assert line["label"].endswith(
            "First Itemized Amount That Exceeds 10% Of All Other Noninterest Income"
        )

    def test_text_only_schedule_raises(self, monkeypatch):
        """A schedule whose only concepts are free text raises ``EmptyDataError``."""
        text_only = {
            "2026-03-31": {
                "name": "WELLS FARGO BANK, NATIONAL ASSOCIATION",
                "form_type": "031",
                "items": [
                    {"mdrm": "TEXT4461", "period": "2026-03-31", "value": "CARD FEES"},
                ],
            }
        }
        _patch(monkeypatch, parsed=text_only)
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.cdr.list_periods",
            lambda product: [{"date": "2026-03-31"}],
        )
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ticker.lead_subsidiary_bank",
            lambda rssd, filers, period: "451965",
        )
        query = FederalReserveCallReportSectionedFetcher.transform_query(
            {"rssd_id": "451965", "section": "Schedule RI-E - Explanations"}
        )
        with pytest.raises(EmptyDataError):
            FederalReserveCallReportSectionedFetcher.extract_data(query, None)

    def test_unresolved_fdic_cert_raises(self, monkeypatch):
        """An FDIC certificate that resolves to nothing raises ``OpenBBError``."""
        _patch(monkeypatch)
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.cdr.resolve_fdic_cert",
            lambda content, cert: None,
        )
        query = FederalReserveCallReportSectionedFetcher.transform_query(
            {"fdic_cert": "0"}
        )
        with pytest.raises(OpenBBError):
            FederalReserveCallReportSectionedFetcher.extract_data(query, None)


class TestTransformData:
    """Tests for ``transform_data``."""

    def test_validates_and_surfaces_metadata(self, monkeypatch):
        """Rows validate; the bank, section, and date land in metadata."""
        _patch(monkeypatch)
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ticker.lead_subsidiary_bank",
            lambda rssd, filers, period: "451965",
        )
        query = FederalReserveCallReportSectionedFetcher.transform_query(
            {"rssd_id": "451965"}
        )
        rows = FederalReserveCallReportSectionedFetcher.extract_data(query, None)
        result = FederalReserveCallReportSectionedFetcher.transform_data(query, rows)
        rows_out = result.result or []
        metadata = result.metadata or {}
        assert all(
            isinstance(r, FederalReserveCallReportSectionedData) for r in rows_out
        )
        assert metadata["rssd_id"] == "451965"
        assert metadata["name"] == "WELLS FARGO BANK, NATIONAL ASSOCIATION"
        assert metadata["section"] == "Schedule RC - Balance Sheet"
        assert metadata["reporting_date"] == "2026-03-31"
        line = next(r for r in rows_out if not r.is_header)
        assert line.label.startswith(">")  # indentation guarded
        assert line.label.endswith("Noninterest-Bearing Balances and Currency and Coin")
        assert line.narrative
        header = next(r for r in rows_out if r.is_header)
        assert header.label == "Schedule RC - Balance Sheet"
        assert header.narrative and header.narrative.startswith(
            "The Report of Condition"
        )

    def test_unknown_section_header_narrative_none(self):
        """A header for a section with no static description keeps a null narrative."""
        query = FederalReserveCallReportSectionedFetcher.transform_query(
            {"rssd_id": "451965"}
        )
        query.section = "Schedule ZZ - Not A Real Schedule"
        data = [
            {
                "label": "Schedule ZZ - Not A Real Schedule",
                "is_header": True,
                "narrative": None,
                "_name": "WELLS FARGO BANK, NATIONAL ASSOCIATION",
                "_rssd": "451965",
                "_periods": ["2026-03-31"],
            },
            {
                "label": "Some line item",
                "is_header": False,
                "narrative": "A definition.",
                "2026-03-31": 1.0,
            },
        ]
        result = FederalReserveCallReportSectionedFetcher.transform_data(query, data)
        header = next(r for r in (result.result or []) if r.is_header)
        assert header.narrative is None

    def test_empty_data_is_validated(self):
        """An empty parsed-row list validates to an empty result without error."""
        query = FederalReserveCallReportSectionedFetcher.transform_query(
            {"rssd_id": "451965"}
        )
        result = FederalReserveCallReportSectionedFetcher.transform_data(query, [])
        assert result.result == []


class TestCallPageDescriptions:
    """Tests for the static Call Report schedule-description map."""

    def test_covers_every_section(self):
        """Every selectable Call schedule has a hover-card description."""
        from openbb_federal_reserve.utils.call_pages import CALL_PAGE_DESCRIPTIONS

        for section in CALL_REPORT_SECTIONS:
            assert CALL_PAGE_DESCRIPTIONS.get(section)
