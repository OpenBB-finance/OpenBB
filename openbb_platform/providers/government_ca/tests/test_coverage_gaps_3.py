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

    def test_extract_data_raises_openbb_error_on_empty_cache(self, monkeypatch):
        """An empty cache raises OpenBBError in the rates fetcher."""
        from openbb_core.app.model.abstract.error import OpenBBError

        from openbb_government_ca.boc.rates import BankOfCanadaRatesFetcher

        GovernmentCaMetadata._reset()
        meta = GovernmentCaMetadata()
        meta._apply_blob(
            {
                "boc": {
                    "series": {},
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

    def test_extract_data_raises_openbb_error_on_empty_cache(self, monkeypatch):
        """An empty cache raises OpenBBError in the yields fetcher."""
        from openbb_core.app.model.abstract.error import OpenBBError

        from openbb_government_ca.boc.yields import BankOfCanadaYieldsFetcher

        GovernmentCaMetadata._reset()
        meta = GovernmentCaMetadata()
        meta._apply_blob(
            {
                "boc": {
                    "series": {},
                    "groups": {},
                },
                "statscan": {},
            }
        )
        try:
            q = BankOfCanadaYieldsFetcher.transform_query({})
            with pytest.raises(OpenBBError, match="No benchmark bond yield"):
                BankOfCanadaYieldsFetcher.extract_data(q, None)
        finally:
            GovernmentCaMetadata._reset()


# ===========================================================================
# statscan/economic_indicators.py — partial branches in date parsing
# ===========================================================================
class TestParseRefperBranches:
    """Cover the ``except ValueError`` branches in date parsing.

    The module was rewritten to fetch observations from the WDS REST
    API. The old ``_parse_refper_to_date`` helper was removed; the
    fetcher now uses ``parse_observation_date`` from
    ``openbb_government_ca.utils.helpers`` (which already has its own
    coverage for these branches in test_coverage_gaps.py).
    """

    def test_parse_observation_date_invalid_month_returns_none(self):
        """``"2024-00"`` returns None via parse_observation_date."""
        from openbb_government_ca.utils.helpers import parse_observation_date

        assert parse_observation_date("2024-00") is None

    def test_parse_observation_date_invalid_month_overflow_returns_none(self):
        """``"2024-13"`` returns None via parse_observation_date."""
        from openbb_government_ca.utils.helpers import parse_observation_date

        assert parse_observation_date("2024-13") is None

    def test_parse_observation_date_year_zero_returns_none(self):
        """``"0000"`` returns None via parse_observation_date."""
        from openbb_government_ca.utils.helpers import parse_observation_date

        assert parse_observation_date("0000") is None
