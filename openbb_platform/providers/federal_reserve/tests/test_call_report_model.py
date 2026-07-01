"""Tests for the FFIEC Bank Call Report (XBRL) fetcher model."""

import io
import zipfile
from datetime import date

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_federal_reserve.models.call_report import (
    FederalReserveCallReportData,
    FederalReserveCallReportFetcher,
    _to_int,
    _to_number,
)

_INSTANCE = (
    '<?xml version="1.0"?>'
    '<xbrl xmlns="http://www.xbrl.org/2003/instance"'
    ' xmlns:xbrli="http://www.xbrl.org/2003/instance"'
    ' xmlns:link="http://www.xbrl.org/2003/linkbase"'
    ' xmlns:xlink="http://www.w3.org/1999/xlink"'
    ' xmlns:cc="https://www.cdr.ffiec.gov/xbrl/call/concepts">'
    '<link:schemaRef xlink:type="simple"'
    ' xlink:href="https://www.cdr.ffiec.gov/xbrl/call/report051/2026-03-31/'
    'v294/call-report051-2026-03-31-v294.xsd"/>'
    '<context id="CI"><entity><identifier scheme="x">37</identifier></entity>'
    "<period><instant>2026-03-31</instant></period></context>"
    '<context id="CD"><entity><identifier scheme="x">37</identifier></entity>'
    "<period><startDate>2026-01-01</startDate>"
    "<endDate>2026-03-31</endDate></period></context>"
    '<unit id="USD"><measure>iso4217:USD</measure></unit>'
    '<unit id="PURE"><measure>pure</measure></unit>'
    '<cc:RCON2170 contextRef="CI" unitRef="USD" decimals="0">4357856</cc:RCON2170>'
    '<cc:RIAD4340 contextRef="CD" unitRef="USD" decimals="0">77000</cc:RIAD4340>'
    '<cc:RCFA7204 contextRef="CI" unitRef="PURE" decimals="4">12.34</cc:RCFA7204>'
    '<cc:RSSD9130 contextRef="CI">Columbus</cc:RSSD9130>'
    "</xbrl>"
)

_LABELS = {
    "RCON2170": "TOTAL ASSETS",
    "RIAD4340": "NET INCOME (LOSS)",
    "RCFA7204": "TIER 1 LEVERAGE RATIO",
}

# Report hierarchy keyed by MDRM, as the presentation linkbase would resolve it.
_HIER = {
    "RIAD4340": {
        "order": 1,
        "section_order": 1,
        "section": "Schedule RI - Income Statement",
        "parent": "Net income",
        "label": "Net income (loss)",
        "level": 2,
    },
    "RCON2170": {
        "order": 1,
        "section_order": 2,
        "section": "Schedule RC - Balance Sheet",
        "parent": "Assets",
        "label": "Total assets",
        "level": 2,
    },
    "RSSD9130": {
        "order": 1,
        "section_order": 3,
        "section": "Bank Demographic Information",
        "parent": None,
        "label": "City",
        "level": 1,
    },
}


def _zip(period: str = "03312026") -> bytes:
    """Build a Call Report XBRL bulk ZIP: a POR roster and one bank instance."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr(
            f"FFIEC CDR Call Bulk POR {period}.txt",
            '"IDRSSD"\tFDIC Certificate Number\tFinancial Institution Name\n'
            "37\t10057\tBANK OF HANCOCK COUNTY\n",
        )
        archive.writestr(f"FFIEC CDR Call FI 37(ID RSSD) {period}.xbrl.xml", _INSTANCE)
    return buffer.getvalue()


def _presentation(report, form_type=None):
    """Stand in for the cached presentation map, asserting the form type."""
    assert form_type == "051"
    return dict(_HIER)


def _patch(monkeypatch):
    """Point the bulk download, MDRM dictionary, and hierarchy at fixtures."""
    monkeypatch.setattr(
        "openbb_federal_reserve.utils.cdr.fetch_bulk",
        lambda product, period=None, fmt="xbrl": _zip(),
    )
    monkeypatch.setattr(
        "openbb_federal_reserve.utils.cdr.presentation_map", _presentation
    )
    monkeypatch.setattr(
        "openbb_federal_reserve.utils.mdrm.fetch_mdrm_dictionary",
        lambda as_of=None, prefix=None: dict(_LABELS),
    )
    monkeypatch.setattr(
        "openbb_federal_reserve.utils.ffiec.entity_type", lambda rssd_id: "NAT"
    )
    monkeypatch.setattr(
        "openbb_federal_reserve.utils.ffiec.fetch_relationships", lambda: []
    )


class TestCoercion:
    """Tests for the value-coercion helpers."""

    def test_to_number_non_numeric(self):
        """A non-numeric value coerces to ``None``; a numeric string parses."""
        assert _to_number("4,357,856") == 4357856.0
        assert _to_number("n/a") is None
        assert _to_number(None) is None

    def test_to_int_non_numeric(self):
        """A non-integer decimals attribute coerces to ``None``."""
        assert _to_int("0") == 0
        assert _to_int("n/a") is None
        assert _to_int(None) is None


class TestTransformQuery:
    """Tests for ``transform_query`` guards."""

    def test_requires_identifier(self):
        """Omitting both rssd_id and fdic_cert raises ``OpenBBError``."""
        with pytest.raises(OpenBBError):
            FederalReserveCallReportFetcher.transform_query({})


class TestExtractData:
    """Tests for the XBRL download, parse, and enrichment."""

    def test_parses_xbrl_facts(self, monkeypatch):
        """The bank's XBRL facts parse with units, period types, and MDRM labels."""
        _patch(monkeypatch)
        query = FederalReserveCallReportFetcher.transform_query({"rssd_id": "37"})
        rows = FederalReserveCallReportFetcher.extract_data(query, None)
        result = FederalReserveCallReportFetcher.transform_data(query, rows).result
        assert all(isinstance(r, FederalReserveCallReportData) for r in result)
        assert all(r.date == date(2026, 3, 31) for r in result)
        by_code = {r.mdrm: r for r in result}
        assets = by_code["RCON2170"]
        assert assets.value == 4357856.0
        assert assets.unit == "USD (thousands)"
        assert assets.period_type == "instant"
        assert by_code["RIAD4340"].period_type == "duration"
        assert by_code["RCFA7204"].unit == "Rate or ratio"
        assert by_code["RCFA7204"].decimals == 4

    def test_demographics_become_metadata(self, monkeypatch):
        """Cover-page concepts go to metadata, not the table; entity type is added."""
        _patch(monkeypatch)
        query = FederalReserveCallReportFetcher.transform_query({"rssd_id": "37"})
        rows = FederalReserveCallReportFetcher.extract_data(query, None)
        annotated = FederalReserveCallReportFetcher.transform_data(query, rows)
        assert "RSSD9130" not in {r.mdrm for r in annotated.result}
        assert annotated.metadata["city"] == "Columbus"
        assert annotated.metadata["entity_type"] == "NAT"
        assert annotated.metadata["form_type"] == "051"
        assert annotated.metadata["rssd_id"] == "37"

    def test_report_order_and_hierarchy(self, monkeypatch):
        """Items sort into report order with the presentation hierarchy."""
        _patch(monkeypatch)
        query = FederalReserveCallReportFetcher.transform_query({"rssd_id": "37"})
        rows = FederalReserveCallReportFetcher.extract_data(query, None)
        result = FederalReserveCallReportFetcher.transform_data(query, rows).result
        # Grouped into schedules (each section a table) in report order; the
        # demographic concept is excluded entirely.
        assert [r.mdrm for r in result] == ["RIAD4340", "RCON2170", "RCFA7204"]
        assert [r.section for r in result] == [
            "Schedule RI - Income Statement",
            "Schedule RC - Balance Sheet",
            "Supplemental Information",
        ]
        # Each section is its own table, so order restarts at 1 within it.
        assert [r.order for r in result] == [1, 1, 1]
        assets = result[1]
        assert assets.parent == "Assets"
        assert assets.level == 2
        assert assets.label == "Total assets"  # presentation caption wins
        # Off-report item falls back to the MDRM label, in a supplemental table.
        assert result[2].label == "TIER 1 LEVERAGE RATIO"
        assert result[2].section == "Supplemental Information"

    def test_period_type_filter(self, monkeypatch):
        """The period_type filter limits to instant or duration items."""
        _patch(monkeypatch)
        query = FederalReserveCallReportFetcher.transform_query(
            {"rssd_id": "37", "period_type": "duration"}
        )
        rows = FederalReserveCallReportFetcher.extract_data(query, None)
        assert {r["mdrm"] for r in rows} == {"RIAD4340"}

    def test_fdic_cert_resolves_to_rssd(self, monkeypatch):
        """An FDIC certificate resolves to the bank's RSSD via the roster."""
        _patch(monkeypatch)
        query = FederalReserveCallReportFetcher.transform_query({"fdic_cert": "10057"})
        rows = FederalReserveCallReportFetcher.extract_data(query, None)
        assert all(r["rssd_id"] == "37" for r in rows)

    def test_symbol_resolves_to_subsidiary_bank(self, monkeypatch):
        """A ticker resolves to the filing bank's RSSD, not the holding company."""
        _patch(monkeypatch)
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ticker.resolve_ticker_to_bank",
            lambda symbol, filers, period=None: "37" if "37" in filers else None,
        )
        query = FederalReserveCallReportFetcher.transform_query({"symbol": "XYZ"})
        rows = FederalReserveCallReportFetcher.extract_data(query, None)
        assert all(r["rssd_id"] == "37" for r in rows)

    def test_holding_company_resolves_to_lead_bank(self, monkeypatch):
        """A holding-company RSSD resolves to its lead subsidiary bank."""
        _patch(monkeypatch)
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ticker.lead_subsidiary_bank",
            lambda rssd, filers, period: "37",
        )
        query = FederalReserveCallReportFetcher.transform_query({"rssd_id": "1039502"})
        rows = FederalReserveCallReportFetcher.extract_data(query, None)
        assert all(r["rssd_id"] == "37" for r in rows)

    def test_unknown_bank_raises(self, monkeypatch):
        """An RSSD that matches no instance raises ``EmptyDataError``."""
        _patch(monkeypatch)
        query = FederalReserveCallReportFetcher.transform_query({"rssd_id": "99999"})
        with pytest.raises(EmptyDataError):
            FederalReserveCallReportFetcher.extract_data(query, None)

    def test_empty_content_raises(self, monkeypatch):
        """Bulk content that is not a ZIP archive raises ``EmptyDataError``."""
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.cdr.fetch_bulk",
            lambda *a, **k: b"not-a-zip",
        )
        query = FederalReserveCallReportFetcher.transform_query({"rssd_id": "37"})
        with pytest.raises(EmptyDataError):
            FederalReserveCallReportFetcher.extract_data(query, None)

    def test_unresolved_symbol_raises(self, monkeypatch):
        """A ticker that resolves to no filing bank raises ``OpenBBError``."""
        _patch(monkeypatch)
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ticker.resolve_ticker_to_bank",
            lambda *a, **k: None,
        )
        query = FederalReserveCallReportFetcher.transform_query({"symbol": "ZZZ"})
        with pytest.raises(OpenBBError):
            FederalReserveCallReportFetcher.extract_data(query, None)

    def test_unresolved_fdic_cert_raises(self, monkeypatch):
        """An FDIC certificate that resolves to no bank raises ``OpenBBError``."""
        _patch(monkeypatch)
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.cdr.resolve_fdic_cert",
            lambda content, cert: None,
        )
        query = FederalReserveCallReportFetcher.transform_query({"fdic_cert": "00000"})
        with pytest.raises(OpenBBError):
            FederalReserveCallReportFetcher.extract_data(query, None)
