"""Final gap-closure tests for 100% coverage.

Each test targets a specific branch identified by the coverage
report's ``BrPart`` column (partial branch coverage).
"""

from __future__ import annotations

from datetime import date

import pytest

from openbb_government_ca.utils.metadata import GovernmentCaMetadata


# ===========================================================================
# boc/rates.py — partial branch coverage on transform_query defaults
# ===========================================================================
class TestRatesTransformQueryBranches:
    """Cover the 'else' branches of the date-default checks.

    The current tests always pass either both dates or neither. We
    need tests that pass only one to cover the partial branches.
    """

    def test_transform_query_with_only_start_date(self):
        """Passing only start_date covers the end_date default branch."""
        from openbb_government_ca.boc.rates import BankOfCanadaRatesFetcher

        q = BankOfCanadaRatesFetcher.transform_query({"start_date": date(2024, 1, 1)})
        assert q.start_date == date(2024, 1, 1)
        assert q.end_date == date.today()  # defaulted

    def test_transform_query_with_only_end_date(self):
        """Passing only end_date covers the start_date default branch."""
        from openbb_government_ca.boc.rates import BankOfCanadaRatesFetcher

        q = BankOfCanadaRatesFetcher.transform_query({"end_date": date(2024, 1, 31)})
        assert q.end_date == date(2024, 1, 31)
        assert q.start_date is not None  # defaulted to 1 year ago

    def test_resolve_target_series_with_cbc20210_present(self, monkeypatch):
        """Cover the branch where CBC20210 IS in matches — returns immediately.

        The current test ``test_prefers_cbc20210_when_both_present``
        covers this, but the coverage report still flags line 168 as
        partial because the loop's `break` isn't always reached in
        the same way. We add an explicit test that asserts the loop
        exits at the first preferred name.
        """
        from openbb_government_ca.boc.rates import BankOfCanadaRatesFetcher

        GovernmentCaMetadata._reset()
        meta = GovernmentCaMetadata()
        meta._apply_blob(
            {
                "boc": {
                    "status": "ok",
                    "series": {
                        "CBC20210": {
                            "name": "CBC20210",
                            "label": "V39079",
                            "description": "Target for the overnight rate",
                            "observations_url": "https://...",
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
            assert entry["name"] == "CBC20210"
        finally:
            GovernmentCaMetadata._reset()

    def test_resolve_target_series_with_only_v39079(self, monkeypatch):
        """Cover the branch where CBC20210 is missing but V39079 is present.

        This exercises the second iteration of the preferred-names loop.
        """
        from openbb_government_ca.boc.rates import BankOfCanadaRatesFetcher

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
                            "observations_url": "https://...",
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

    def test_extract_data_falls_back_to_direct_lookup(self, monkeypatch):
        """Cover the branch where description lookup fails but direct name lookup succeeds.

        This is the path on rates.py line 168: ``if entry is None``
        (after the description search returned None) — we then try
        direct lookup by preferred name and succeed.
        """
        from unittest.mock import patch

        from openbb_government_ca.boc.rates import BankOfCanadaRatesFetcher

        GovernmentCaMetadata._reset()
        meta = GovernmentCaMetadata()
        # Build a cache where CBC20210 exists but its description
        # is empty/missing — so the description lookup returns None,
        # but the direct name lookup succeeds.
        meta._apply_blob(
            {
                "boc": {
                    "status": "ok",
                    "series": {
                        "CBC20210": {
                            "name": "CBC20210",
                            "label": "V39079",
                            "description": "",  # empty — description lookup returns None
                            "observations_url": "https://www.bankofcanada.ca/valet/observations/CBC20210/json",
                        },
                    },
                    "groups": {},
                },
                "statscan": {},
            }
        )
        # Mock the HTTP call so we don't actually hit the network.
        fake_payload = {
            "observations": [
                {"d": "2024-01-02", "CBC20210": {"v": "5.00"}},
            ]
        }
        try:
            with patch(
                "openbb_government_ca.boc.rates.http_get_json",
                return_value=fake_payload,
            ):
                q = BankOfCanadaRatesFetcher.transform_query({})
                raw = BankOfCanadaRatesFetcher.extract_data(q, None)
            # Should have found CBC20210 via direct name lookup.
            assert len(raw) >= 1
            assert raw[0]["_series"] == "CBC20210"
        finally:
            GovernmentCaMetadata._reset()

    def test_extract_data_raises_openbb_error_in_degraded_mode(self, monkeypatch):
        """A degraded cache raises OpenBBError in the rates fetcher.

        Covers the ``if is_degraded(boc_cache): raise OpenBBError(...)``
        branch on line 168 of rates.py.
        """
        from openbb_core.app.model.abstract.error import OpenBBError

        from openbb_government_ca.boc.rates import BankOfCanadaRatesFetcher

        GovernmentCaMetadata._reset()
        meta = GovernmentCaMetadata()
        meta._apply_blob(
            {
                "boc": {
                    "status": "degraded",
                    "warning": "boc down",
                    "series": {},
                    "groups": {},
                },
                "statscan": {},
            }
        )
        try:
            q = BankOfCanadaRatesFetcher.transform_query({})
            with pytest.raises(OpenBBError, match="degraded mode"):
                BankOfCanadaRatesFetcher.extract_data(q, None)
        finally:
            GovernmentCaMetadata._reset()


# ===========================================================================
# boc/yields.py — partial branch coverage on transform_query defaults
# ===========================================================================
class TestYieldsTransformQueryBranches:
    """Cover the 'else' branches of the date-default checks."""

    def test_transform_query_with_only_start_date(self):
        """Passing only start_date covers the end_date default branch."""
        from openbb_government_ca.boc.yields import BankOfCanadaYieldsFetcher

        q = BankOfCanadaYieldsFetcher.transform_query({"start_date": date(2024, 1, 1)})
        assert q.start_date == date(2024, 1, 1)
        assert q.end_date == date.today()

    def test_transform_query_with_only_end_date(self):
        """Passing only end_date covers the start_date default branch."""
        from openbb_government_ca.boc.yields import BankOfCanadaYieldsFetcher

        q = BankOfCanadaYieldsFetcher.transform_query({"end_date": date(2024, 1, 31)})
        assert q.end_date == date(2024, 1, 31)
        assert q.start_date is not None

    def test_extract_data_raises_openbb_error_in_degraded_mode(self, monkeypatch):
        """A degraded cache raises OpenBBError in the yields fetcher.

        Covers the ``if is_degraded(boc_cache): raise OpenBBError(...)``
        branch on line 202 of yields.py.
        """
        from openbb_core.app.model.abstract.error import OpenBBError

        from openbb_government_ca.boc.yields import BankOfCanadaYieldsFetcher

        GovernmentCaMetadata._reset()
        meta = GovernmentCaMetadata()
        meta._apply_blob(
            {
                "boc": {
                    "status": "degraded",
                    "warning": "boc down",
                    "series": {},
                    "groups": {},
                },
                "statscan": {},
            }
        )
        try:
            q = BankOfCanadaYieldsFetcher.transform_query({})
            with pytest.raises(OpenBBError, match="degraded mode"):
                BankOfCanadaYieldsFetcher.extract_data(q, None)
        finally:
            GovernmentCaMetadata._reset()


# ===========================================================================
# statscan/economic_indicators.py — partial branches in _parse_refper_to_date
# ===========================================================================
class TestParseRefperBranches:
    """Cover the ``except ValueError`` branches in _parse_refper_to_date."""

    def test_monthly_with_zero_month_raises_value_error(self):
        """``"2024-00"`` → month=0 → date(2024, 0, 1) raises ValueError.

        This covers the ``except ValueError: return None`` branch in
        the monthly parser.
        """
        from openbb_government_ca.statscan.economic_indicators import (
            _parse_refper_to_date,
        )

        assert _parse_refper_to_date("2024-00") is None

    def test_monthly_with_month_thirteen_raises_value_error(self):
        """``"2024-13"`` → month=13 → date(2024, 13, 1) raises ValueError."""
        from openbb_government_ca.statscan.economic_indicators import (
            _parse_refper_to_date,
        )

        assert _parse_refper_to_date("2024-13") is None

    def test_monthly_with_year_zero_raises_value_error(self):
        """``"0000-01"`` → year=0 → date(0, 1, 1) raises ValueError.

        This covers the same branch with a different trigger.
        """
        from openbb_government_ca.statscan.economic_indicators import (
            _parse_refper_to_date,
        )

        assert _parse_refper_to_date("0000-01") is None

    def test_monthly_with_year_overflow_raises_value_error(self):
        """``"99999-01"`` doesn't enter the monthly branch (len != 7).

        Actually, len("99999-01") == 8, so this doesn't enter monthly.
        We need a 4-char year that overflows date(). There isn't one
        in 4-char space (max 9999). So this branch is unreachable via
        the monthly path — it's only reachable via the annual path,
        which has its own except. We cover the annual except here.
        """
        from openbb_government_ca.statscan.economic_indicators import (
            _parse_refper_to_date,
        )

        # Annual: "0000" → date(0, 1, 1) raises ValueError.
        assert _parse_refper_to_date("0000") is None

    def test_monthly_with_non_digit_year_after_month(self):
        """``"September abcd"`` → year_str isn't digits → loop continues.

        This covers the partial branch ``132->128`` (the if condition
        was False, so we go back to the loop instead of returning).
        """
        from openbb_government_ca.statscan.economic_indicators import (
            _parse_refper_to_date,
        )

        assert _parse_refper_to_date("September abcd") is None

    def test_monthly_with_wrong_length_year(self):
        """``"September 201"`` → year_str is digits but len != 4 → loop continues.

        This covers the same partial branch with a different trigger.
        """
        from openbb_government_ca.statscan.economic_indicators import (
            _parse_refper_to_date,
        )

        assert _parse_refper_to_date("September 201") is None

    def test_monthly_with_year_zero_after_month_name(self):
        """``"September 0000"`` → year=0 → date(0, 1, 1) raises ValueError.

        This covers the ``except ValueError: return None`` branch on
        lines 135-136 of economic_indicators.py. The year "0000" is
        digits and length 4, so it passes the if-check, but
        ``date(0, 1, 1)`` raises ValueError because year 0 is out of
        range.
        """
        from openbb_government_ca.statscan.economic_indicators import (
            _parse_refper_to_date,
        )

        assert _parse_refper_to_date("September 0000") is None

    def test_monthly_with_year_overflow_after_month_name(self):
        """``"September 99999"`` → year_str is digits but len=5 → loop continues.

        Covers the partial branch where the if is False due to length.
        """
        from openbb_government_ca.statscan.economic_indicators import (
            _parse_refper_to_date,
        )

        # "September 99999" — len("99999")==5, so the if is False.
        # The loop continues but no other month name matches, so
        # returns None at the end.
        assert _parse_refper_to_date("September 99999") is None
