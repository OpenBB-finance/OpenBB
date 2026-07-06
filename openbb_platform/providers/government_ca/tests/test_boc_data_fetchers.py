"""Tests for the BoC runtime data fetchers (Phase 5).

Covers:
- ``BankOfCanadaFXFetcher`` (obb.boc.fx → currency_historical)
- ``BankOfCanadaRatesFetcher`` (obb.boc.rates → country_interest_rates)
- ``BankOfCanadaYieldsFetcher`` (obb.boc.yields → treasury_rates)

These fetchers read from the shipped metadata cache AND make runtime
HTTP calls to the BoC Valet API for observations. Tests mock
``http_get_json`` so no network is hit.

Normalization rules verified per the Phase 5 matrix:
- fx:       close = raw value (NO /100 — FX is direct price)
- rates:    value = raw / 100 (matches OECD pattern + x-frontend_multiply:100)
- yields:   year_N = raw / 100 (per model docstring "1% = 0.01")
"""

from __future__ import annotations

from datetime import date
from unittest.mock import patch

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_government_ca.boc.fx import BankOfCanadaFXFetcher
from openbb_government_ca.boc.rates import BankOfCanadaRatesFetcher
from openbb_government_ca.boc.yields import BankOfCanadaYieldsFetcher
from openbb_government_ca.utils._http import NetworkError


# ---------------------------------------------------------------------------
# Helper: build a synthetic Valet observations payload
# ---------------------------------------------------------------------------
def _boc_obs_payload(series_name: str, observations: list[tuple[str, str]]) -> dict:
    """Build a synthetic Valet ``/observations/<SERIES>/json`` payload.

    ``observations`` is a list of ``(date_str, value_str)`` tuples.
    """
    return {
        "terms": {"url": "https://www.bankofcanada.ca/terms/"},
        "seriesDetail": {
            series_name: {
                "label": series_name,
                "description": "",
                "dimension": {"key": "d", "name": "Date"},
            }
        },
        "observations": [
            {"d": d_str, series_name: {"v": v_str}} for d_str, v_str in observations
        ],
    }


# ===========================================================================
# BankOfCanadaFXFetcher
# ===========================================================================
class TestBankOfCanadaFXFetcher:
    """``obb.boc.fx`` — FX rates, mapped to ``currency_historical``."""

    def test_transform_query_normalizes_symbol(self):
        """The symbol is normalized to the BoC canonical ``FX{BASE}{QUOTE}`` form."""
        q = BankOfCanadaFXFetcher.transform_query({"symbol": "USD/CAD"})
        assert q.symbol == "FXUSDCAD"

    def test_transform_query_applies_date_defaults(self):
        """If no dates are provided, defaults to last 30 days."""
        q = BankOfCanadaFXFetcher.transform_query({"symbol": "FXUSDCAD"})
        assert q.start_date is not None
        assert q.end_date == date.today()
        # start_date should be ~30 days ago.
        delta = date.today() - q.start_date
        assert 25 <= delta.days <= 35

    def test_transform_query_preserves_explicit_dates(self):
        """Explicit dates are preserved."""
        q = BankOfCanadaFXFetcher.transform_query(
            {
                "symbol": "FXUSDCAD",
                "start_date": date(2024, 1, 1),
                "end_date": date(2024, 1, 31),
            }
        )
        assert q.start_date == date(2024, 1, 1)
        assert q.end_date == date(2024, 1, 31)

    def test_extract_data_returns_observations(self, seeded_meta):
        """A successful fetch returns the raw observation list."""
        payload = _boc_obs_payload(
            "FXUSDCAD",
            [("2024-01-02", "1.3316"), ("2024-01-03", "1.3356")],
        )
        with patch("openbb_government_ca.boc.fx.http_get_json", return_value=payload):
            q = BankOfCanadaFXFetcher.transform_query(
                {
                    "symbol": "FXUSDCAD",
                    "start_date": date(2024, 1, 1),
                    "end_date": date(2024, 1, 5),
                }
            )
            result = BankOfCanadaFXFetcher.extract_data(q, None)
        assert len(result) == 2
        assert result[0]["d"] == "2024-01-02"

    def test_transform_data_populates_close_only(self, seeded_meta):
        """Per the brief: ``close`` is filled, OHLC left as ``None``."""
        payload = _boc_obs_payload(
            "FXUSDCAD",
            [("2024-01-02", "1.3316"), ("2024-01-03", "1.3356")],
        )
        with patch("openbb_government_ca.boc.fx.http_get_json", return_value=payload):
            q = BankOfCanadaFXFetcher.transform_query({"symbol": "FXUSDCAD"})
            raw = BankOfCanadaFXFetcher.extract_data(q, None)
            result = BankOfCanadaFXFetcher.transform_data(q, raw)
        assert len(result) == 2
        for row in result:
            assert row.close is not None  # populated
            assert row.open is None  # brief: OHLC left as None
            assert row.high is None
            assert row.low is None
            assert row.volume is None
            assert row.vwap is None
            assert row.series == "FXUSDCAD"

    def test_value_not_normalized(self, seeded_meta):
        """FX values are NOT divided by 100 — they are direct prices."""
        payload = _boc_obs_payload("FXUSDCAD", [("2024-01-02", "1.3316")])
        with patch("openbb_government_ca.boc.fx.http_get_json", return_value=payload):
            q = BankOfCanadaFXFetcher.transform_query({"symbol": "FXUSDCAD"})
            raw = BankOfCanadaFXFetcher.extract_data(q, None)
            result = BankOfCanadaFXFetcher.transform_data(q, raw)
        # 1.3316 → 1.3316 (NO division)
        assert result[0].close == 1.3316

    def test_sorts_ascending_by_date(self, seeded_meta):
        """Results are sorted ascending by date."""
        payload = _boc_obs_payload(
            "FXUSDCAD",
            [("2024-01-05", "1.34"), ("2024-01-02", "1.33"), ("2024-01-03", "1.335")],
        )
        with patch("openbb_government_ca.boc.fx.http_get_json", return_value=payload):
            q = BankOfCanadaFXFetcher.transform_query({"symbol": "FXUSDCAD"})
            raw = BankOfCanadaFXFetcher.extract_data(q, None)
            result = BankOfCanadaFXFetcher.transform_data(q, raw)
        dates = [r.date for r in result]
        assert dates == sorted(dates)

    def test_skips_empty_observations(self, seeded_meta):
        """BoC uses empty string for holidays — those rows are skipped."""
        payload = _boc_obs_payload(
            "FXUSDCAD",
            [("2024-01-01", ""), ("2024-01-02", "1.3316")],  # Jan 1 = holiday
        )
        with patch("openbb_government_ca.boc.fx.http_get_json", return_value=payload):
            q = BankOfCanadaFXFetcher.transform_query({"symbol": "FXUSDCAD"})
            raw = BankOfCanadaFXFetcher.extract_data(q, None)
            result = BankOfCanadaFXFetcher.transform_data(q, raw)
        assert len(result) == 1  # holiday row skipped

    def test_raises_openbb_error_for_empty_cache(self, empty_meta):
        """An empty cache raises ``OpenBBError`` when series not found."""
        q = BankOfCanadaFXFetcher.transform_query({"symbol": "FXUSDCAD"})
        with pytest.raises(OpenBBError, match="not found in cache"):
            BankOfCanadaFXFetcher.extract_data(q, None)

    def test_raises_openbb_error_for_unknown_symbol(self, seeded_meta):
        """An unknown symbol raises ``OpenBBError`` (not bare ``KeyError``)."""
        q = BankOfCanadaFXFetcher.transform_query({"symbol": "FXZZZCAD"})
        with pytest.raises(OpenBBError, match="not found in cache"):
            BankOfCanadaFXFetcher.extract_data(q, None)

    def test_raises_openbb_error_on_network_failure(self, seeded_meta):
        """A network failure is wrapped in ``OpenBBError``."""
        with patch(
            "openbb_government_ca.boc.fx.http_get_json",
            side_effect=NetworkError("https://...", "connection failed"),
        ):
            q = BankOfCanadaFXFetcher.transform_query({"symbol": "FXUSDCAD"})
            with pytest.raises(OpenBBError, match="Failed to fetch"):
                BankOfCanadaFXFetcher.extract_data(q, None)

    def test_raises_empty_data_for_no_observations(self, seeded_meta):
        """If BoC returns no observations, raises ``EmptyDataError``."""
        with patch(
            "openbb_government_ca.boc.fx.http_get_json",
            return_value={"observations": []},
        ):
            q = BankOfCanadaFXFetcher.transform_query({"symbol": "FXUSDCAD"})
            with pytest.raises(EmptyDataError, match="no observations"):
                BankOfCanadaFXFetcher.extract_data(q, None)

    def test_full_round_trip(self, seeded_meta):
        """End-to-end ``fetcher.test()`` runs without error."""
        payload = _boc_obs_payload("FXUSDCAD", [("2024-01-02", "1.3316")])
        with patch("openbb_government_ca.boc.fx.http_get_json", return_value=payload):
            fetcher = BankOfCanadaFXFetcher()
            result = fetcher.test({"symbol": "FXUSDCAD"}, {})
        assert result is None


# ===========================================================================
# BankOfCanadaRatesFetcher
# ===========================================================================
class TestBankOfCanadaRatesFetcher:
    """``obb.boc.rates`` — policy overnight rate target, mapped to ``country_interest_rates``."""

    def test_transform_query_locks_country_to_canada(self):
        """The country field is always 'canada' for this fetcher."""
        q = BankOfCanadaRatesFetcher.transform_query({})
        assert q.country == "canada"

    def test_transform_query_applies_date_defaults(self):
        """Defaults to 1 year ago → today."""
        q = BankOfCanadaRatesFetcher.transform_query({})
        delta = date.today() - q.start_date
        assert 360 <= delta.days <= 370

    def test_prefers_cbc20210_when_both_present(self, seeded_meta):
        """When both CBC20210 and V39079 are in the cache, CBC20210 wins.

        This is the user's explicit Phase 5 directive — the brief
        mentions CBC20210, so we prefer it for disambiguation.
        """
        entry = BankOfCanadaRatesFetcher._resolve_target_series(seeded_meta.boc)
        assert entry is not None
        assert entry["name"] == "CBC20210"

    def test_falls_back_to_v39079_when_cbc_missing(self, monkeypatch):
        """When only V39079 is in the cache, it's used."""
        from openbb_government_ca.utils.metadata import GovernmentCaMetadata

        GovernmentCaMetadata._reset()
        meta = GovernmentCaMetadata()
        meta._apply_blob(
            {
                "boc": {
                    "status": "ok",
                    "series": {
                        "V39079": {
                            "name": "V39079",
                            "label": "V39079",
                            "description": "Target for the overnight rate",
                            "observations_url": "https://www.bankofcanada.ca/valet/observations/V39079/json",
                        },
                    },
                    "groups": {},
                },
                "statscan": {},
            }
        )
        try:
            entry = BankOfCanadaRatesFetcher._resolve_target_series(meta.boc)
            assert entry is not None
            assert entry["name"] == "V39079"
        finally:
            GovernmentCaMetadata._reset()

    def test_value_normalized_to_decimal(self, seeded_meta):
        """The rate is divided by 100: 5.00 → 0.05.

        This matches the OECD fetcher pattern and the model's
        ``x-frontend_multiply: 100`` directive.
        """
        payload = _boc_obs_payload("CBC20210", [("2024-01-02", "5.00")])
        with patch(
            "openbb_government_ca.boc.rates.http_get_json", return_value=payload
        ):
            q = BankOfCanadaRatesFetcher.transform_query({})
            raw = BankOfCanadaRatesFetcher.extract_data(q, None)
            result = BankOfCanadaRatesFetcher.transform_data(q, raw)
        # 5.00 → 0.05 (divided by 100)
        assert result[0].value == 0.05
        assert result[0].country == "canada"
        assert result[0].series == "CBC20210"

    def test_multiple_observations_sorted_ascending(self, seeded_meta):
        """Multiple days are sorted ascending by date."""
        payload = _boc_obs_payload(
            "CBC20210",
            [("2024-01-05", "5.00"), ("2024-01-02", "4.75"), ("2024-01-03", "4.75")],
        )
        with patch(
            "openbb_government_ca.boc.rates.http_get_json", return_value=payload
        ):
            q = BankOfCanadaRatesFetcher.transform_query({})
            raw = BankOfCanadaRatesFetcher.extract_data(q, None)
            result = BankOfCanadaRatesFetcher.transform_data(q, raw)
        assert len(result) == 3
        assert result[0].date == date(2024, 1, 2)
        assert result[-1].date == date(2024, 1, 5)

    def test_raises_openbb_error_when_no_target_series_found(self, monkeypatch):
        """If no series matches the target description, raises ``OpenBBError``."""
        from openbb_government_ca.utils.metadata import GovernmentCaMetadata

        GovernmentCaMetadata._reset()
        meta = GovernmentCaMetadata()
        meta._apply_blob(
            {
                "boc": {
                    "status": "ok",
                    "series": {
                        "FXUSDCAD": {
                            "name": "FXUSDCAD",
                            "label": "USD/CAD",
                            "description": "Daily average exchange rate",
                            "observations_url": "https://...",
                        },
                    },
                    "groups": {},
                },
                "statscan": {},
            }
        )
        try:
            q = BankOfCanadaRatesFetcher.transform_query({})
            with pytest.raises(OpenBBError, match="Could not find"):
                BankOfCanadaRatesFetcher.extract_data(q, None)
        finally:
            GovernmentCaMetadata._reset()

    def test_raises_empty_data_for_no_observations(self, seeded_meta):
        """If BoC returns no observations, raises ``EmptyDataError``."""
        with patch(
            "openbb_government_ca.boc.rates.http_get_json",
            return_value={"observations": []},
        ):
            q = BankOfCanadaRatesFetcher.transform_query({})
            with pytest.raises(EmptyDataError):
                BankOfCanadaRatesFetcher.extract_data(q, None)

    def test_full_round_trip(self, seeded_meta):
        """End-to-end ``fetcher.test()`` runs without error."""
        payload = _boc_obs_payload("CBC20210", [("2024-01-02", "5.00")])
        with patch(
            "openbb_government_ca.boc.rates.http_get_json", return_value=payload
        ):
            fetcher = BankOfCanadaRatesFetcher()
            result = fetcher.test({}, {})
        assert result is None


# ===========================================================================
# BankOfCanadaYieldsFetcher
# ===========================================================================
class TestBankOfCanadaYieldsFetcher:
    """``obb.boc.yields`` — benchmark bond yields, mapped to ``treasury_rates``."""

    def test_transform_query_applies_date_defaults(self):
        """Defaults to 1 year ago → today."""
        q = BankOfCanadaYieldsFetcher.transform_query({})
        delta = date.today() - q.start_date
        assert 360 <= delta.days <= 370

    def test_resolve_bond_series_uses_tenor_years(self, seeded_meta):
        """Bond series are grouped by ``tenor_years`` from the cache.

        Only series with a non-None ``tenor_years`` are included.
        """
        # The seeded cache only has BD.CDN.10YR.DQ.YLD with tenor_years=10.
        # Add a few more bond series to the cache for a fuller test.
        from openbb_government_ca.utils.metadata import GovernmentCaMetadata

        GovernmentCaMetadata._reset()
        meta = GovernmentCaMetadata()
        meta._apply_blob(
            {
                "boc": {
                    "status": "ok",
                    "series": {
                        "BD.CDN.2YR.DQ.YLD": {
                            "name": "BD.CDN.2YR.DQ.YLD",
                            "tenor_years": 2,
                            "observations_url": "https://.../2YR/json",
                        },
                        "BD.CDN.10YR.DQ.YLD": {
                            "name": "BD.CDN.10YR.DQ.YLD",
                            "tenor_years": 10,
                            "observations_url": "https://.../10YR/json",
                        },
                        "BD.CDN.LONG.DQ.YLD": {
                            "name": "BD.CDN.LONG.DQ.YLD",
                            "tenor_years": 30,
                            "observations_url": "https://.../LONG/json",
                        },
                        "BD.CDN.RRB.DQ.YLD": {
                            "name": "BD.CDN.RRB.DQ.YLD",
                            "tenor_years": None,  # excluded — no nominal tenor
                            "observations_url": "https://.../RRB/json",
                        },
                        "FXUSDCAD": {
                            "name": "FXUSDCAD",
                            "tenor_years": None,  # not a bond
                            "observations_url": "https://.../FXUSDCAD/json",
                        },
                    },
                    "groups": {},
                },
                "statscan": {},
            }
        )
        try:
            bond_series = BankOfCanadaYieldsFetcher._resolve_bond_series(meta.boc)
            # 3 bonds (2Y, 10Y, LONG) — RRB and FX are excluded.
            assert set(bond_series.keys()) == {2, 10, 30}
        finally:
            GovernmentCaMetadata._reset()

    def test_pivots_observations_by_date(self, monkeypatch):
        """Multiple tenors on the same date become one row."""
        from openbb_government_ca.utils.metadata import GovernmentCaMetadata

        GovernmentCaMetadata._reset()
        meta = GovernmentCaMetadata()
        meta._apply_blob(
            {
                "boc": {
                    "status": "ok",
                    "series": {
                        "BD.CDN.2YR.DQ.YLD": {
                            "name": "BD.CDN.2YR.DQ.YLD",
                            "tenor_years": 2,
                            "observations_url": "https://.../2YR/json",
                        },
                        "BD.CDN.10YR.DQ.YLD": {
                            "name": "BD.CDN.10YR.DQ.YLD",
                            "tenor_years": 10,
                            "observations_url": "https://.../10YR/json",
                        },
                    },
                    "groups": {},
                },
                "statscan": {},
            }
        )
        try:
            payloads = {
                "https://.../2YR/json": _boc_obs_payload(
                    "BD.CDN.2YR.DQ.YLD", [("2024-01-02", "4.50")]
                ),
                "https://.../10YR/json": _boc_obs_payload(
                    "BD.CDN.10YR.DQ.YLD", [("2024-01-02", "3.75")]
                ),
            }

            def _fake_http_get_json(url, **kwargs):
                return payloads.get(url, {"observations": []})

            with patch(
                "openbb_government_ca.boc.yields.http_get_json",
                side_effect=_fake_http_get_json,
            ):
                q = BankOfCanadaYieldsFetcher.transform_query({})
                raw = BankOfCanadaYieldsFetcher.extract_data(q, None)
                result = BankOfCanadaYieldsFetcher.transform_data(q, raw)

            # One row for 2024-01-02 with both tenors filled.
            assert len(result) == 1
            row = result[0]
            assert row.date == date(2024, 1, 2)
            # Values normalized: 4.50 → 0.045, 3.75 → 0.0375
            assert row.year_2 == 0.045
            assert row.year_10 == 0.0375
            # Other tenors are None (not fetched).
            assert row.year_3 is None
            assert row.year_5 is None
            assert row.year_7 is None
            assert row.year_30 is None
            # Sub-1Y fields are always None per the brief.
            assert row.week_4 is None
            assert row.month_1 is None
            assert row.month_3 is None
            assert row.month_6 is None
            assert row.year_1 is None
            assert row.year_20 is None
        finally:
            GovernmentCaMetadata._reset()

    def test_value_normalized_to_decimal(self, monkeypatch):
        """Yields are divided by 100: 3.18 → 0.0318 (per model docstring '1% = 0.01')."""
        from openbb_government_ca.utils.metadata import GovernmentCaMetadata

        GovernmentCaMetadata._reset()
        meta = GovernmentCaMetadata()
        meta._apply_blob(
            {
                "boc": {
                    "status": "ok",
                    "series": {
                        "BD.CDN.10YR.DQ.YLD": {
                            "name": "BD.CDN.10YR.DQ.YLD",
                            "tenor_years": 10,
                            "observations_url": "https://.../10YR/json",
                        },
                    },
                    "groups": {},
                },
                "statscan": {},
            }
        )
        try:
            payload = _boc_obs_payload("BD.CDN.10YR.DQ.YLD", [("2024-01-02", "3.18")])
            with patch(
                "openbb_government_ca.boc.yields.http_get_json", return_value=payload
            ):
                q = BankOfCanadaYieldsFetcher.transform_query({})
                raw = BankOfCanadaYieldsFetcher.extract_data(q, None)
                result = BankOfCanadaYieldsFetcher.transform_data(q, raw)
            # 3.18 → 0.0318 (divided by 100)
            assert result[0].year_10 == 0.0318
        finally:
            GovernmentCaMetadata._reset()

    def test_skips_empty_observations(self, monkeypatch):
        """Empty values (holidays) are skipped, not zero."""
        from openbb_government_ca.utils.metadata import GovernmentCaMetadata

        GovernmentCaMetadata._reset()
        meta = GovernmentCaMetadata()
        meta._apply_blob(
            {
                "boc": {
                    "status": "ok",
                    "series": {
                        "BD.CDN.10YR.DQ.YLD": {
                            "name": "BD.CDN.10YR.DQ.YLD",
                            "tenor_years": 10,
                            "observations_url": "https://.../10YR/json",
                        },
                    },
                    "groups": {},
                },
                "statscan": {},
            }
        )
        try:
            payload = _boc_obs_payload(
                "BD.CDN.10YR.DQ.YLD",
                [("2024-01-01", ""), ("2024-01-02", "3.18")],  # Jan 1 = holiday
            )
            with patch(
                "openbb_government_ca.boc.yields.http_get_json", return_value=payload
            ):
                q = BankOfCanadaYieldsFetcher.transform_query({})
                raw = BankOfCanadaYieldsFetcher.extract_data(q, None)
                result = BankOfCanadaYieldsFetcher.transform_data(q, raw)
            assert len(result) == 1  # holiday row skipped
        finally:
            GovernmentCaMetadata._reset()

    def test_partial_failure_leaves_tenor_none(self, monkeypatch):
        """If one tenor's HTTP call fails, that field stays ``None``.

        We don't raise — partial results are still useful to the user.
        """
        from openbb_government_ca.utils.metadata import GovernmentCaMetadata

        GovernmentCaMetadata._reset()
        meta = GovernmentCaMetadata()
        meta._apply_blob(
            {
                "boc": {
                    "status": "ok",
                    "series": {
                        "BD.CDN.2YR.DQ.YLD": {
                            "name": "BD.CDN.2YR.DQ.YLD",
                            "tenor_years": 2,
                            "observations_url": "https://.../2YR/json",
                        },
                        "BD.CDN.10YR.DQ.YLD": {
                            "name": "BD.CDN.10YR.DQ.YLD",
                            "tenor_years": 10,
                            "observations_url": "https://.../10YR/json",
                        },
                    },
                    "groups": {},
                },
                "statscan": {},
            }
        )
        try:

            def _fake_http_get_json(url, **kwargs):
                if "10YR" in url:
                    raise NetworkError(url, "10YR endpoint down")
                return _boc_obs_payload("BD.CDN.2YR.DQ.YLD", [("2024-01-02", "4.50")])

            with patch(
                "openbb_government_ca.boc.yields.http_get_json",
                side_effect=_fake_http_get_json,
            ):
                q = BankOfCanadaYieldsFetcher.transform_query({})
                raw = BankOfCanadaYieldsFetcher.extract_data(q, None)
                result = BankOfCanadaYieldsFetcher.transform_data(q, raw)
            # We still got the 2Y row, just with year_10=None.
            assert len(result) >= 1
            assert result[0].year_2 == 0.045
            assert result[0].year_10 is None
        finally:
            GovernmentCaMetadata._reset()

    def test_raises_openbb_error_when_no_bond_series_in_cache(self, empty_meta):
        """If the cache has no bond series, raises ``OpenBBError``."""
        q = BankOfCanadaYieldsFetcher.transform_query({})
        with pytest.raises(OpenBBError, match="No benchmark bond yield series"):
            BankOfCanadaYieldsFetcher.extract_data(q, None)

    def test_raises_empty_data_when_all_calls_return_nothing(self, monkeypatch):
        """If all HTTP calls return empty observations, raises ``EmptyDataError``."""
        from openbb_government_ca.utils.metadata import GovernmentCaMetadata

        GovernmentCaMetadata._reset()
        meta = GovernmentCaMetadata()
        meta._apply_blob(
            {
                "boc": {
                    "status": "ok",
                    "series": {
                        "BD.CDN.10YR.DQ.YLD": {
                            "name": "BD.CDN.10YR.DQ.YLD",
                            "tenor_years": 10,
                            "observations_url": "https://.../10YR/json",
                        },
                    },
                    "groups": {},
                },
                "statscan": {},
            }
        )
        try:
            with patch(
                "openbb_government_ca.boc.yields.http_get_json",
                return_value={"observations": []},
            ):
                q = BankOfCanadaYieldsFetcher.transform_query({})
                with pytest.raises(EmptyDataError):
                    BankOfCanadaYieldsFetcher.extract_data(q, None)
        finally:
            GovernmentCaMetadata._reset()

    def test_fetched_tenors_field_populated(self, monkeypatch):
        """The ``fetched_tenors`` extension field lists which tenors succeeded."""
        from openbb_government_ca.utils.metadata import GovernmentCaMetadata

        GovernmentCaMetadata._reset()
        meta = GovernmentCaMetadata()
        meta._apply_blob(
            {
                "boc": {
                    "status": "ok",
                    "series": {
                        "BD.CDN.2YR.DQ.YLD": {
                            "name": "BD.CDN.2YR.DQ.YLD",
                            "tenor_years": 2,
                            "observations_url": "https://.../2YR/json",
                        },
                        "BD.CDN.10YR.DQ.YLD": {
                            "name": "BD.CDN.10YR.DQ.YLD",
                            "tenor_years": 10,
                            "observations_url": "https://.../10YR/json",
                        },
                    },
                    "groups": {},
                },
                "statscan": {},
            }
        )
        try:
            payloads = {
                "https://.../2YR/json": _boc_obs_payload(
                    "BD.CDN.2YR.DQ.YLD", [("2024-01-02", "4.50")]
                ),
                "https://.../10YR/json": _boc_obs_payload(
                    "BD.CDN.10YR.DQ.YLD", [("2024-01-02", "3.75")]
                ),
            }

            def _fake_http_get_json(url, **kwargs):
                return payloads.get(url, {"observations": []})

            with patch(
                "openbb_government_ca.boc.yields.http_get_json",
                side_effect=_fake_http_get_json,
            ):
                q = BankOfCanadaYieldsFetcher.transform_query({})
                raw = BankOfCanadaYieldsFetcher.extract_data(q, None)
                result = BankOfCanadaYieldsFetcher.transform_data(q, raw)
            assert "2Y" in result[0].fetched_tenors
            assert "10Y" in result[0].fetched_tenors
        finally:
            GovernmentCaMetadata._reset()
