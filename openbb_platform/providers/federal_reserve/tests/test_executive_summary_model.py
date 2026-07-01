"""Tests for the FFIEC Executive Summary Report (ESR, CDR router) model."""

import re

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_federal_reserve.models.executive_summary import (
    FederalReserveExecutiveSummaryData,
    FederalReserveExecutiveSummaryFetcher,
)

from .ffiec_cassettes import CASSETTE_DIR, replay

_ESR_CASSETTE = "executive_summary"
_ESR_RSSD_ID = "852218"
_ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

_ROWS = [
    {"label": "Income Statement $:", "is_header": True},
    {
        "label": "Net Interest Income",
        "is_header": False,
        "2026-03-31": 13105000.0,
        "2025-12-31": 13363000.0,
    },
    {
        "label": "Net Income",
        "is_header": False,
        "2026-03-31": 5961000.0,
        "2025-12-31": 6236000.0,
    },
]


def _patch(monkeypatch, result=None, resolved=None):
    """Point the report fetch and the lead-bank resolver at in-memory fixtures."""
    source = _ROWS if result is None else result
    monkeypatch.setattr(
        "openbb_federal_reserve.utils.executive_summary_report.fetch_executive_summary",
        lambda rssd_id, **kwargs: [dict(row) for row in source],
    )
    monkeypatch.setattr(
        "openbb_federal_reserve.utils.ticker.resolve_rssd_to_bank",
        lambda rssd_id: resolved if resolved is not None else (str(rssd_id), None),
    )


class TestTransformQuery:
    """Tests for ``transform_query``."""

    def test_requires_identifier(self):
        """Omitting both symbol and rssd_id raises ``OpenBBError``."""
        with pytest.raises(OpenBBError):
            FederalReserveExecutiveSummaryFetcher.transform_query({})

    def test_accepts_rssd_id(self):
        """An rssd_id is carried onto the query."""
        query = FederalReserveExecutiveSummaryFetcher.transform_query(
            {"rssd_id": "451965"}
        )
        assert query.rssd_id == "451965"


class TestExtractData:
    """Tests for ``extract_data``."""

    def test_returns_rows(self, monkeypatch):
        """The report's rows pass through from the router client."""
        _patch(monkeypatch)
        query = FederalReserveExecutiveSummaryFetcher.transform_query(
            {"rssd_id": "451965"}
        )
        assert len(FederalReserveExecutiveSummaryFetcher.extract_data(query, None)) == 3

    def test_empty_raises(self, monkeypatch):
        """An empty report raises ``EmptyDataError``."""
        _patch(monkeypatch, [])
        query = FederalReserveExecutiveSummaryFetcher.transform_query(
            {"rssd_id": "451965"}
        )
        with pytest.raises(EmptyDataError):
            FederalReserveExecutiveSummaryFetcher.extract_data(query, None)

    def test_symbol_resolves_to_rssd(self, monkeypatch):
        """A ticker resolves to an RSSD before the report fetch."""
        _patch(monkeypatch)
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ticker.resolve_ticker_to_rssd",
            lambda symbol: "451965",
        )
        query = FederalReserveExecutiveSummaryFetcher.transform_query({"symbol": "WFC"})
        assert len(FederalReserveExecutiveSummaryFetcher.extract_data(query, None)) == 3

    def test_unresolved_symbol_raises(self, monkeypatch):
        """A ticker that resolves to nothing raises ``OpenBBError``."""
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ticker.resolve_ticker_to_rssd",
            lambda symbol: None,
        )
        query = FederalReserveExecutiveSummaryFetcher.transform_query({"symbol": "ZZZ"})
        with pytest.raises(OpenBBError):
            FederalReserveExecutiveSummaryFetcher.extract_data(query, None)


class TestAllPeriods:
    """Tests for the ``all_periods`` query parameter."""

    def test_param_default_false(self):
        """The ``all_periods`` flag defaults to False."""
        query = FederalReserveExecutiveSummaryFetcher.transform_query(
            {"rssd_id": "451965"}
        )
        assert query.all_periods is False

    def test_param_threads_to_client(self, monkeypatch):
        """``all_periods=True`` is forwarded to the report fetch."""
        captured: dict = {}

        def _fetch(rssd_id, **kwargs):
            """Capture the kwargs handed to the client fetch."""
            captured.update(kwargs)
            return [dict(row) for row in _ROWS]

        monkeypatch.setattr(
            "openbb_federal_reserve.utils.executive_summary_report"
            ".fetch_executive_summary",
            _fetch,
        )
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ticker.resolve_rssd_to_bank",
            lambda rssd_id: (str(rssd_id), None),
        )
        query = FederalReserveExecutiveSummaryFetcher.transform_query(
            {"rssd_id": "451965", "all_periods": True}
        )
        FederalReserveExecutiveSummaryFetcher.extract_data(query, None)
        assert captured.get("all_periods") is True


class TestTransformData:
    """Tests for ``transform_data``."""

    def test_validates_wide_rows(self, monkeypatch):
        """Line items carry per-period values; headers carry only a label."""
        _patch(monkeypatch)
        query = FederalReserveExecutiveSummaryFetcher.transform_query(
            {"rssd_id": "451965"}
        )
        rows = FederalReserveExecutiveSummaryFetcher.extract_data(query, None)
        result = FederalReserveExecutiveSummaryFetcher.transform_data(query, rows)
        out = result.result or []
        assert all(isinstance(r, FederalReserveExecutiveSummaryData) for r in out)
        line = next(r for r in out if not r.is_header)
        assert line.model_dump()["2026-03-31"] == 13105000.0
        header = next(r for r in out if r.is_header)
        assert header.label == "Income Statement $:"

    def test_bank_rssd_surfaces_only_its_rssd(self, monkeypatch):
        """A bank RSSD that already files surfaces only its own RSSD in metadata."""
        _patch(monkeypatch)
        query = FederalReserveExecutiveSummaryFetcher.transform_query(
            {"rssd_id": "451965"}
        )
        rows = FederalReserveExecutiveSummaryFetcher.extract_data(query, None)
        result = FederalReserveExecutiveSummaryFetcher.transform_data(query, rows)
        metadata = result.metadata or {}
        assert metadata == {"rssd_id": "451965"}

    def test_holding_company_resolves_and_surfaces_bank(self, monkeypatch):
        """A holding-company RSSD resolves to its lead bank, surfaced in metadata."""
        _patch(monkeypatch, resolved=("852218", "JPMORGAN CHASE BANK NA"))
        query = FederalReserveExecutiveSummaryFetcher.transform_query(
            {"rssd_id": "1039502"}
        )
        rows = FederalReserveExecutiveSummaryFetcher.extract_data(query, None)
        result = FederalReserveExecutiveSummaryFetcher.transform_data(query, rows)
        metadata = result.metadata or {}
        assert metadata == {"rssd_id": "852218", "name": "JPMORGAN CHASE BANK NA"}

    def test_no_bank_report_shell_raises(self, monkeypatch):
        """A resolved RSSD whose rows carry no period values raises the bank error."""
        _patch(
            monkeypatch,
            [
                {"label": "Income Statement $:", "is_header": True},
                {
                    "label": "Net Income",
                    "is_header": False,
                    "narrative": "Net income for the period.",
                    "2026-03-31": None,
                },
            ],
        )
        query = FederalReserveExecutiveSummaryFetcher.transform_query(
            {"rssd_id": "2162966"}
        )
        with pytest.raises(OpenBBError) as exc:
            FederalReserveExecutiveSummaryFetcher.extract_data(query, None)
        assert "No Executive Summary data for RSSD 2162966" in str(exc.value)

    def test_empty_data_validates_without_metadata(self):
        """An empty parsed-row list validates to an empty result with no metadata."""
        query = FederalReserveExecutiveSummaryFetcher.transform_query(
            {"rssd_id": "451965"}
        )
        result = FederalReserveExecutiveSummaryFetcher.transform_data(query, [])
        assert result.result == []
        assert result.metadata == {}


class TestExecutiveSummaryCassette:
    """Replay the captured ESR transports through the full real fetcher."""

    @pytest.fixture(scope="class")
    def parsed(self):
        """Run transform_query -> extract_data -> transform_data over the cassette.

        Serves the router responses, parsed guide concepts and filtered concept
        index entirely from the recording, so the parse runs with no live network
        and no pre-warmed cache. The Call Report filer set is served as the bank's
        own RSSD so the lead-bank resolution is a no-op and never hits the network.
        """
        with pytest.MonkeyPatch.context() as patch, replay(_ESR_CASSETTE):
            patch.setattr(
                "openbb_federal_reserve.utils.ticker.call_report_filers",
                lambda: {_ESR_RSSD_ID},
            )
            query = FederalReserveExecutiveSummaryFetcher.transform_query(
                {"rssd_id": _ESR_RSSD_ID}
            )
            raw = FederalReserveExecutiveSummaryFetcher.extract_data(query, None)
            result = FederalReserveExecutiveSummaryFetcher.transform_data(query, raw)
            return result.result or []

    def test_cassette_is_plain_text_json(self):
        """The captured cassette is readable plain-text JSON, never binary."""
        import json

        path = CASSETTE_DIR / f"{_ESR_CASSETTE}.json"
        store = json.loads(path.read_text(encoding="utf-8"))
        assert isinstance(store, dict) and store
        assert any(k.startswith("post ReportSectionData") for k in store)

    def test_parse_yields_validated_rows(self, parsed):
        """Every replayed row validates into the report's data model."""
        assert parsed
        assert all(isinstance(r, FederalReserveExecutiveSummaryData) for r in parsed)

    def test_real_section_headers_present(self, parsed):
        """The eight published ESR sections surface as real header rows."""
        headers = [r.label for r in parsed if r.is_header]
        assert "Income Statement $:" in headers
        assert "Earnings and Profitability:" in headers
        assert "Capitalization:" in headers
        assert len(headers) >= 6

    def test_real_line_labels_resolved(self, parsed):
        """Line labels are resolved to real concept names, not the synthetic stubs."""
        labels = {r.label for r in parsed if not r.is_header}
        assert "Net Interest Income for the Quarter" in labels
        assert "Total Assets" in labels
        assert "#SectionTitle#" not in "".join(labels)
        synthetic = {"Net Interest Income", "Net Income", "Income Statement $:"}
        assert not (labels & synthetic)

    def test_iso_period_columns_carry_real_values(self, parsed):
        """Line rows carry ISO-dated period columns populated with real floats."""
        period_cols: set[str] = set()
        for row in parsed:
            period_cols.update(k for k in row.model_dump() if _ISO_DATE.match(k))
        assert len(period_cols) == 5
        assert "2026-03-31" in period_cols

        line = next(
            r
            for r in parsed
            if not r.is_header and r.label == "Net Interest Income for the Quarter"
        )
        dumped = line.model_dump()
        values = {k: dumped[k] for k in period_cols if dumped.get(k) is not None}
        assert len(values) == 5
        assert all(isinstance(v, float) and v != 0.0 for v in values.values())
        assert dumped["2026-03-31"] == 25316000000.0

    def test_narratives_resolved_from_guide(self, parsed):
        """The recorded guide concepts resolve real concept narratives onto rows."""
        lines = [r for r in parsed if not r.is_header]
        with_narrative = [r for r in lines if r.narrative]
        assert len(with_narrative) >= len(lines) // 2
        assert all(
            isinstance(r.narrative, str) and r.narrative.strip() for r in with_narrative
        )
