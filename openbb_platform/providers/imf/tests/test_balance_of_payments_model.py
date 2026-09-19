"""Tests for the IMF Balance of Payments Fetcher."""

# ruff: noqa: I001

from datetime import date as dateType

import pytest

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_imf.models.balance_of_payments import (
    ImfBalanceOfPaymentsData,
    ImfBalanceOfPaymentsFetcher,
    ImfBalanceOfPaymentsQueryParams,
)


def _row(
    indicator: str, entry: str, period: str, value: float, country: str = "Japan"
) -> dict:
    """Return a single SDMX long-form row as the query builder emits."""
    return {
        "INDICATOR_code": indicator,
        "BOP_ACCOUNTING_ENTRY_code": entry,
        "COUNTRY_label": country,
        "TIME_PERIOD": period,
        "OBS_VALUE": value,
    }


def _decomposed_rows() -> list[dict]:
    """Build a complete two-period decomposition for the unit-test scenarios."""
    return [
        _row("CAB", "NETCD_T", "2024-03-31", -200.0),
        _row("CAB", "NETCD_T", "2024-06-30", -300.0),
        _row("G", "NETCD_T", "2024-03-31", -250.0),
        _row("G", "NETCD_T", "2024-06-30", -280.0),
        _row("G", "CD_T", "2024-03-31", 500.0),
        _row("G", "CD_T", "2024-06-30", 520.0),
        _row("G", "DB_T", "2024-03-31", 750.0),
        _row("G", "DB_T", "2024-06-30", 800.0),
        _row("S", "NETCD_T", "2024-03-31", 75.0),
        _row("S", "NETCD_T", "2024-06-30", 70.0),
        _row("S", "CD_T", "2024-03-31", 260.0),
        _row("S", "CD_T", "2024-06-30", 280.0),
        _row("S", "DB_T", "2024-03-31", 185.0),
        _row("S", "DB_T", "2024-06-30", 210.0),
        _row("IN1", "NETCD_T", "2024-03-31", -10.0),
        _row("IN1", "NETCD_T", "2024-06-30", -15.0),
        _row("IN1", "CD_T", "2024-03-31", 350.0),
        _row("IN1", "CD_T", "2024-06-30", 365.0),
        _row("IN1", "DB_T", "2024-03-31", 360.0),
        _row("IN1", "DB_T", "2024-06-30", 380.0),
        _row("IN2", "NETCD_T", "2024-03-31", -50.0),
        _row("IN2", "NETCD_T", "2024-06-30", -55.0),
        _row("IN2", "CD_T", "2024-03-31", 48.0),
        _row("IN2", "CD_T", "2024-06-30", 47.0),
        _row("IN2", "DB_T", "2024-03-31", 98.0),
        _row("IN2", "DB_T", "2024-06-30", 102.0),
    ]


class TestQueryParams:
    """Tests for ``ImfBalanceOfPaymentsQueryParams``."""

    def test_default_country_resolves(self):
        """``united_states`` (label) resolves to ``USA`` (ISO3)."""
        q = ImfBalanceOfPaymentsQueryParams()
        assert q.country == "USA"
        assert q.frequency == "quarterly"

    def test_country_list_joined_with_plus(self):
        """Comma-separated tokens join with ``+`` and ISO3 codes pass through."""
        q = ImfBalanceOfPaymentsQueryParams(country="USA,japan")
        assert q.country == "USA+JPN"

    def test_invalid_country_raises(self):
        """An unknown country token raises ``ValueError``."""
        with pytest.raises(
            ValueError, match="not in the IMF BOP dataflow's country list"
        ):
            ImfBalanceOfPaymentsQueryParams(country="not_a_country")

    def test_transform_query_passes_through(self):
        """``transform_query`` constructs the params model from a dict."""
        q = ImfBalanceOfPaymentsFetcher.transform_query(
            {"country": "USA", "frequency": "annual"}
        )
        assert isinstance(q, ImfBalanceOfPaymentsQueryParams)
        assert q.country == "USA"
        assert q.frequency == "annual"

    def test_country_list_comes_from_bop_dataflow(self):
        """``BOP_CODE_SET`` / ``BOP_LABEL_TO_CODE`` are derived from the BOP dataflow."""
        from openbb_imf.models.balance_of_payments import (
            BOP_CODE_SET,
            BOP_LABEL_TO_CODE,
        )
        from openbb_imf.utils.metadata import ImfMetadata

        params = ImfMetadata().get_dataflow_parameters("BOP")
        live_codes = {p["value"].upper() for p in params.get("COUNTRY", [])}
        assert live_codes == BOP_CODE_SET
        assert set(BOP_LABEL_TO_CODE.values()) == live_codes
        assert BOP_LABEL_TO_CODE["united_states"] == "USA"

    def test_country_loader_skips_entries_without_value(self):
        """Country entries missing ``value`` are skipped by the loader."""
        from openbb_imf.models import balance_of_payments as bop_mod

        class _Stub:
            """In-memory stand-in for ``ImfMetadata``."""

            def get_dataflow_parameters(self, _dataflow_id):
                """Return one valid + one missing-value entry."""
                return {
                    "COUNTRY": [
                        {"value": "USA", "label": "United States"},
                        {"value": "", "label": "Skipped"},
                        {"label": "No Value"},
                    ]
                }

        original = bop_mod.ImfMetadata
        bop_mod.ImfMetadata = _Stub  # type: ignore[assignment]
        try:
            label_to_code, code_set = bop_mod._load_bop_countries()
        finally:
            bop_mod.ImfMetadata = original  # type: ignore[assignment]

        assert code_set == {"USA"}
        assert label_to_code == {"united_states": "USA"}


class TestExtractData:
    """Tests for ``ImfBalanceOfPaymentsFetcher.extract_data``."""

    def _mock_builder(self, monkeypatch, rows):
        """Patch ``ImfQueryBuilder`` to record fetch calls and return canned rows."""
        from openbb_imf.utils import query_builder as qb

        calls: list[dict] = []

        class _Stub:
            def fetch_data(self, dataflow, **kwargs):
                """Record the call and return canned rows."""
                calls.append({"dataflow": dataflow, **kwargs})
                return {"data": list(rows), "metadata": {}}

        monkeypatch.setattr(qb, "ImfQueryBuilder", _Stub)
        return calls

    def test_single_skip_validation_call(self, monkeypatch):
        """Extract issues exactly one SDMX call with ``_skip_validation=True``."""
        calls = self._mock_builder(monkeypatch, _decomposed_rows())
        q = ImfBalanceOfPaymentsQueryParams(
            country="JPN",
            frequency="quarterly",
            start_date=dateType(2024, 1, 1),
            end_date=dateType(2024, 12, 31),
        )
        rows = ImfBalanceOfPaymentsFetcher.extract_data(q, {})
        assert len(calls) == 1
        call = calls[0]
        assert call["dataflow"] == "BOP"
        assert call["COUNTRY"] == "JPN"
        assert call["UNIT"] == "USD"
        assert call["FREQUENCY"] == "Q"
        assert call["start_date"] == "2024-01-01"
        assert call["end_date"] == "2024-12-31"
        assert call["_skip_validation"] is True
        assert call["INDICATOR"] == "CAB+G+S+IN1+IN2"
        assert call["BOP_ACCOUNTING_ENTRY"] == "NETCD_T+CD_T+DB_T"
        assert len(rows) == len(_decomposed_rows())

    def test_omits_unset_dates(self, monkeypatch):
        """Missing date params surface as ``None`` to the query builder."""
        calls = self._mock_builder(monkeypatch, _decomposed_rows())
        q = ImfBalanceOfPaymentsQueryParams(country="JPN")
        ImfBalanceOfPaymentsFetcher.extract_data(q, {})
        assert calls[0]["start_date"] is None
        assert calls[0]["end_date"] is None

    def test_annual_frequency_maps_to_A(self, monkeypatch):
        """``annual`` maps to the SDMX ``A`` code."""
        calls = self._mock_builder(monkeypatch, _decomposed_rows())
        q = ImfBalanceOfPaymentsQueryParams(country="JPN", frequency="annual")
        ImfBalanceOfPaymentsFetcher.extract_data(q, {})
        assert calls[0]["FREQUENCY"] == "A"

    def test_empty_result_raises(self, monkeypatch):
        """An empty inner-fetcher result raises ``OpenBBError``."""
        self._mock_builder(monkeypatch, [])
        q = ImfBalanceOfPaymentsQueryParams(country="JPN")
        with pytest.raises(OpenBBError, match="No BOP data"):
            ImfBalanceOfPaymentsFetcher.extract_data(q, {})

    def test_openbb_error_propagates(self, monkeypatch):
        """An ``OpenBBError`` from the inner fetch is re-raised."""
        from openbb_imf.utils import query_builder as qb

        class _Stub:
            def fetch_data(self, *_a, **_kw):
                """Always raise."""
                raise OpenBBError("boom")

        monkeypatch.setattr(qb, "ImfQueryBuilder", _Stub)
        q = ImfBalanceOfPaymentsQueryParams(country="JPN")
        with pytest.raises(OpenBBError, match="boom"):
            ImfBalanceOfPaymentsFetcher.extract_data(q, {})

    def test_value_error_wraps_to_openbb_error(self, monkeypatch):
        """A ``ValueError`` from the query builder wraps to ``OpenBBError``."""
        from openbb_imf.utils import query_builder as qb

        class _Stub:
            def fetch_data(self, *_a, **_kw):
                """Always raise."""
                raise ValueError("bad dim")

        monkeypatch.setattr(qb, "ImfQueryBuilder", _Stub)
        q = ImfBalanceOfPaymentsQueryParams(country="JPN")
        with pytest.raises(OpenBBError, match="bad dim"):
            ImfBalanceOfPaymentsFetcher.extract_data(q, {})

    def test_handles_non_dict_result_gracefully(self, monkeypatch):
        """A non-dict return from the builder is treated as no data."""
        from openbb_imf.utils import query_builder as qb

        class _Stub:
            def fetch_data(self, *_a, **_kw):
                """Return a non-dict sentinel."""
                return None

        monkeypatch.setattr(qb, "ImfQueryBuilder", _Stub)
        q = ImfBalanceOfPaymentsQueryParams(country="JPN")
        with pytest.raises(OpenBBError, match="No BOP data"):
            ImfBalanceOfPaymentsFetcher.extract_data(q, {})


class TestTransformData:
    """Tests for ``ImfBalanceOfPaymentsFetcher.transform_data``."""

    def test_pivots_into_bp6_columns(self):
        """All recognised (indicator, entry) pairs populate the BP6 fields."""
        q = ImfBalanceOfPaymentsQueryParams(country="JPN")
        out = ImfBalanceOfPaymentsFetcher.transform_data(q, _decomposed_rows())
        assert len(out) == 2
        first = out[0]
        assert first.period == dateType(2024, 3, 31)
        assert first.country == "Japan"
        assert first.balance_total == -200.0
        assert first.balance_total_goods == -250.0
        assert first.balance_total_services == 75.0
        assert first.credits_total_goods == 500.0
        assert first.credits_total_services == 260.0
        assert first.credits_total == 500.0 + 260.0 + 350.0 + 48.0
        assert first.debits_total == 750.0 + 185.0 + 360.0 + 98.0
        assert first.credits_services_percent_of_goods_and_services == pytest.approx(
            260.0 / (260.0 + 500.0)
        )
        assert first.credits_services_percent_of_current_account == pytest.approx(
            260.0 / first.credits_total
        )
        assert first.debits_services_percent_of_goods_and_services == pytest.approx(
            185.0 / (185.0 + 750.0)
        )
        assert first.debits_services_percent_of_current_account == pytest.approx(
            185.0 / first.debits_total
        )

    def test_ignores_unrecognised_indicator_or_entry(self):
        """Rows for unknown indicator codes or accounting entries are dropped."""
        rows = [
            _row("UNKNOWN", "NETCD_T", "2024-03-31", 1.0),
            _row("G", "X_OTHER", "2024-03-31", 2.0),
            _row("G", "NETCD_T", "2024-03-31", 42.0),
        ]
        q = ImfBalanceOfPaymentsQueryParams(country="JPN")
        out = ImfBalanceOfPaymentsFetcher.transform_data(q, rows)
        assert len(out) == 1
        assert out[0].balance_total_goods == 42.0

    def test_skips_bad_values_and_dates(self):
        """Missing / unparsable values and empty dates are skipped."""
        rows = [
            _row("G", "NETCD_T", "2024-03-31", None),
            _row("G", "NETCD_T", "", 5.0),
            {
                "INDICATOR_code": "G",
                "BOP_ACCOUNTING_ENTRY_code": "NETCD_T",
                "TIME_PERIOD": "2024-06-30",
                "OBS_VALUE": "not-a-number",
                "COUNTRY_label": "Japan",
            },
            _row("G", "NETCD_T", "2024-12-31", 99.0),
        ]
        q = ImfBalanceOfPaymentsQueryParams(country="JPN")
        out = ImfBalanceOfPaymentsFetcher.transform_data(q, rows)
        assert len(out) == 1
        assert out[0].period == dateType(2024, 12, 31)
        assert out[0].balance_total_goods == 99.0

    def test_partial_components_skip_synthesised_totals(self):
        """When a credits/debits component is missing, totals stay ``None``."""
        rows = [_row("G", "CD_T", "2024-03-31", 100.0)]
        q = ImfBalanceOfPaymentsQueryParams(country="JPN")
        out = ImfBalanceOfPaymentsFetcher.transform_data(q, rows)
        assert out[0].credits_total is None
        assert out[0].credits_services_percent_of_goods_and_services is None

    def test_country_falls_back_to_code_then_iso(self):
        """``COUNTRY_label`` is preferred; ``COUNTRY_code`` and ``COUNTRY`` fall back."""
        rows = [
            {
                "INDICATOR_code": "G",
                "BOP_ACCOUNTING_ENTRY_code": "NETCD_T",
                "TIME_PERIOD": "2024-03-31",
                "OBS_VALUE": 1.0,
                "COUNTRY_code": "JPN",
            },
            {
                "INDICATOR_code": "S",
                "BOP_ACCOUNTING_ENTRY_code": "NETCD_T",
                "TIME_PERIOD": "2024-03-31",
                "OBS_VALUE": 2.0,
                "COUNTRY": "USA",
            },
        ]
        q = ImfBalanceOfPaymentsQueryParams(country="JPN,USA")
        countries = {
            r.country for r in ImfBalanceOfPaymentsFetcher.transform_data(q, rows)
        }
        assert countries == {"JPN", "USA"}

    def test_sorts_by_period_then_country(self):
        """Output is sorted ascending by date, then country."""
        rows = [
            _row("G", "NETCD_T", "2024-06-30", 1.0, country="USA"),
            _row("G", "NETCD_T", "2024-03-31", 2.0, country="USA"),
            _row("G", "NETCD_T", "2024-03-31", 3.0, country="JPN"),
        ]
        q = ImfBalanceOfPaymentsQueryParams(country="USA,japan")
        out = ImfBalanceOfPaymentsFetcher.transform_data(q, rows)
        assert [(r.period, r.country) for r in out] == [
            (dateType(2024, 3, 31), "JPN"),
            (dateType(2024, 3, 31), "USA"),
            (dateType(2024, 6, 30), "USA"),
        ]


class TestImfBalanceOfPaymentsData:
    """Sanity tests for the standardised data model."""

    def test_alias_period_maps_to_date(self):
        """The ``date`` alias populates the standard ``period`` field."""
        d = ImfBalanceOfPaymentsData.model_validate(
            {"date": dateType(2024, 3, 31), "country": "USA"}
        )
        assert d.period == dateType(2024, 3, 31)
        assert d.country == "USA"

    def test_model_dump_uses_bpm6_canonical_order(self):
        """``model_dump`` emits keys in BPM6 reading order."""
        d = ImfBalanceOfPaymentsData.model_validate(
            {
                "period": dateType(2024, 3, 31),
                "country": "USA",
                "balance_total": 1.0,
                "balance_total_goods": 2.0,
                "balance_total_services": 3.0,
                "credits_total": 4.0,
                "debits_total": 5.0,
            }
        )
        keys = list(d.model_dump(exclude_none=True).keys())
        assert keys == [
            "period",
            "country",
            "balance_total",
            "balance_total_goods",
            "balance_total_services",
            "credits_total",
            "debits_total",
        ]
