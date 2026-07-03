"""Bank of Canada — Benchmark Government of Canada Bond Yields.

This fetcher reads from the shipped metadata cache (Phase 3) to find
the benchmark bond yield series (2Y, 3Y, 5Y, 7Y, 10Y, 30Y/LONG),
then makes parallel runtime HTTP calls to fetch each series'
observations and pivots them into a single ``treasury_rates``-shaped
row per date.

Maps to OpenBB's standard ``treasury_rates`` model. Per the brief:
- ``year_2``, ``year_3``, ``year_5``, ``year_7``, ``year_10``,
  ``year_30`` are populated from the corresponding BoC series.
- All sub-1Y fields (``week_4``, ``month_1``, ``month_2``,
  ``month_3``, ``month_6``, ``year_1``) and ``year_20`` are left as
  ``None`` — the BoC doesn't publish benchmark series for those
  tenors.
- Values are normalized to decimals (3.18 → 0.0318) per the model's
  docstring: "All fields are expressed as a normalized percent - 1% = 0.01".

Design notes
------------
- **Tenor resolution via the cache.** The cache (Phase 3) carries a
  derived ``tenor_years`` field on each bond series, parsed from the
  series name with a regex. The fetcher groups bond series by
  ``tenor_years`` and uses that to map directly to the
  ``treasury_rates.year_<N>`` fields — no hard-coded series names.
- **Parallel fetch.** Each tenor is a separate Valet endpoint, so we
  issue all calls in parallel via ``concurrent.futures.ThreadPoolExecutor``
  to keep latency reasonable. Failures in individual tenors are
  logged but don't fail the whole request — that tenor just stays
  ``None``.
- **Pivot.** The Valet API returns one observation list per series.
  We pivot by date: each unique date becomes one ``TreasuryRatesData``
  row with all available tenors filled in.
"""

from __future__ import annotations

import concurrent.futures as cf
from datetime import date, timedelta
from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.treasury_rates import (
    TreasuryRatesData,
    TreasuryRatesQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

from openbb_government_ca.boc.utils import is_degraded, list_series
from openbb_government_ca.utils._http import NetworkError, http_get_json
from openbb_government_ca.utils.metadata import GovernmentCaMetadata

# Map from tenor_years → treasury_rates field name. We only support
# the tenors the BoC actually publishes as nominal benchmarks. The
# sub-1Y fields (week_4, month_1..6, year_1) and year_20 are left as
# None per the brief.
_TENOR_YEARS_TO_FIELD: dict[int, str] = {
    2: "year_2",
    3: "year_3",
    5: "year_5",
    7: "year_7",
    10: "year_10",
    30: "year_30",  # BD.CDN.LONG.DQ.YLD ≈ 30y
}

# Max parallel HTTP calls to Valet. 6 is a safe default — Valet
# doesn't document a rate limit but we don't want to hammer it.
_MAX_PARALLEL_FETCH = 6


def _default_start_date() -> date:
    """Return 1 year ago as a default start_date."""
    return date.today() - timedelta(days=365)


class BankOfCanadaYieldsQueryParams(TreasuryRatesQueryParams):
    """BoC Benchmark Bond Yields Query.

    Extends the standard ``TreasuryRatesQueryParams`` with BoC defaults.
    The brief locks the country implicitly to Canada (the model has no
    ``country`` field — yields are Canada-only by definition of the
    BoC benchmark series).
    """

    start_date: date | None = Field(
        default=None,
        description="Start date (YYYY-MM-DD). Defaults to 1 year ago.",
    )
    end_date: date | None = Field(
        default=None,
        description="End date (YYYY-MM-DD). Defaults to today.",
    )


class BankOfCanadaYieldsData(TreasuryRatesData):
    """BoC Benchmark Bond Yields Data.

    Extends the standard ``TreasuryRatesData`` with a BoC-specific
    extension field listing the tenors that were actually fetched
    (useful for debugging partial failures).
    """

    fetched_tenors: list[str] | None = Field(
        default=None,
        description="List of tenor labels actually fetched (e.g. ['2Y', '10Y', 'LONG']).",
    )


class BankOfCanadaYieldsFetcher(
    Fetcher[BankOfCanadaYieldsQueryParams, list[BankOfCanadaYieldsData]]
):
    """BoC Benchmark Bond Yields Fetcher.

    Reads the cache to find bond series, fetches each tenor's
    observations in parallel, then pivots by date into a single
    ``treasury_rates``-shaped row per observation date.
    """

    @staticmethod
    def transform_query(params: dict[str, Any]) -> BankOfCanadaYieldsQueryParams:
        """Transform raw params into a validated query model."""
        transformed = params.copy()
        if transformed.get("start_date") is None:
            transformed["start_date"] = _default_start_date()
        if transformed.get("end_date") is None:
            transformed["end_date"] = date.today()
        return BankOfCanadaYieldsQueryParams(**transformed)

    @staticmethod
    def _resolve_bond_series(boc_cache: dict) -> dict[int, dict[str, Any]]:
        """Return ``{tenor_years: series_entry}`` for every cataloged bond.

        Only series with a non-None ``tenor_years`` are included —
        this excludes RRB (Real Return Bonds, inflation-linked) and
        any non-bond series.
        """
        bond_series: dict[int, dict[str, Any]] = {}
        for entry in list_series(boc_cache):
            tenor_years = entry.get("tenor_years")
            if tenor_years is None:
                continue
            # Only include tenors we know how to map.
            if int(tenor_years) not in _TENOR_YEARS_TO_FIELD:
                continue
            bond_series[int(tenor_years)] = entry
        return bond_series

    @staticmethod
    def _fetch_single_tenor(
        entry: dict[str, Any],
        start_date: date,
        end_date: date,
    ) -> tuple[int, list[dict]]:
        """Fetch observations for a single bond series. Returns ``(tenor_years, observations)``.

        On network failure, returns ``(tenor_years, [])`` — the tenor
        is just left as ``None`` in the final output. We don't raise
        because partial results are still useful to the user.
        """
        tenor_years = int(entry.get("tenor_years", 0))
        observations_url = entry.get("observations_url", "")
        if not observations_url:
            return (tenor_years, [])

        params: dict[str, str] = {
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
        }
        try:
            payload = http_get_json(observations_url, params=params, timeout=30.0)
        except NetworkError:
            # Silent failure — partial result is better than aborting.
            return (tenor_years, [])

        observations = (
            payload.get("observations", []) if isinstance(payload, dict) else []
        )
        # Tag each observation with the tenor for the pivot step.
        for obs in observations:
            obs["_tenor_years"] = tenor_years
            obs["_series_name"] = entry.get("name", "")
        return (tenor_years, observations)

    @staticmethod
    def extract_data(
        query: BankOfCanadaYieldsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Fetch observations for all bond tenors in parallel.

        Returns a flat list of observations, each tagged with its
        ``_tenor_years``. The pivot into ``treasury_rates`` rows
        happens in ``transform_data``.
        """
        meta = GovernmentCaMetadata()
        boc_cache = meta.boc

        if is_degraded(boc_cache):
            raise OpenBBError(
                "Bank of Canada metadata cache is in degraded mode — the "
                "package was built when www.bankofcanada.ca was unreachable. "
                "Reinstall openbb-government-ca with "
                "OPENBB_GOVERNMENT_CA_FORCE_CACHE_REBUILD=1 to retry."
            )

        bond_series = BankOfCanadaYieldsFetcher._resolve_bond_series(boc_cache)
        if not bond_series:
            raise OpenBBError(
                "No benchmark bond yield series found in the cache. The cache "
                "should contain BD.CDN.{2YR,3YR,5YR,7YR,10YR,LONG}.DQ.YLD — "
                "reinstall the package if these are missing."
            )

        # ``transform_query`` always populates these with defaults.
        assert query.start_date is not None  # noqa: S101
        assert query.end_date is not None  # noqa: S101

        # Fetch all tenors in parallel. Each call is independent.
        all_observations: list[dict] = []
        with cf.ThreadPoolExecutor(max_workers=_MAX_PARALLEL_FETCH) as executor:
            futures = [
                executor.submit(
                    BankOfCanadaYieldsFetcher._fetch_single_tenor,
                    entry,
                    query.start_date,
                    query.end_date,
                )
                for entry in bond_series.values()
            ]
            for future in cf.as_completed(futures):
                _tenor, obs_list = future.result()
                all_observations.extend(obs_list)

        if not all_observations:
            raise EmptyDataError(
                f"BoC returned no bond yield observations in the date range "
                f"{query.start_date} to {query.end_date}."
            )

        return all_observations

    @staticmethod
    def transform_data(
        query: BankOfCanadaYieldsQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[BankOfCanadaYieldsData]:
        """Pivot flat observations into ``treasury_rates`` rows by date.

        Each unique date becomes one row. The ``year_<N>`` field is
        filled from the observation with matching ``_tenor_years``.
        Missing tenors stay ``None``.
        """
        # Group observations by date.
        by_date: dict[date, dict[int, float]] = {}
        fetched_tenors: set[str] = set()
        for obs in data:
            obs_date_str = obs.get("d")
            if not obs_date_str:
                continue
            try:
                obs_date = date.fromisoformat(str(obs_date_str))
            except ValueError:
                continue
            tenor_years = obs.get("_tenor_years")
            if tenor_years is None:
                continue
            series_name = str(obs.get("_series_name", ""))
            series_block = obs.get(series_name, {})
            value_str = (
                series_block.get("v") if isinstance(series_block, dict) else None
            )
            if value_str is None or value_str == "":
                continue
            try:
                raw_value = float(value_str)
            except (TypeError, ValueError):
                continue
            # Normalize to decimal — 3.18 → 0.0318. Per the model
            # docstring: "1% = 0.01".
            normalized = raw_value / 100.0
            by_date.setdefault(obs_date, {})[int(tenor_years)] = normalized

            # Track which tenor labels actually got data.
            for ty, field_name in _TENOR_YEARS_TO_FIELD.items():
                if int(tenor_years) == ty:
                    label = (
                        f"{ty}Y" if ty != 30 else "LONG"
                    )  # 30Y maps to BD.CDN.LONG.DQ.YLD
                    fetched_tenors.add(label)

        # Build one row per date.
        output: list[BankOfCanadaYieldsData] = []
        for obs_date in sorted(by_date.keys()):
            tenor_values = by_date[obs_date]
            row_kwargs: dict[str, Any] = {"date": obs_date}
            for tenor_years, field_name in _TENOR_YEARS_TO_FIELD.items():
                row_kwargs[field_name] = tenor_values.get(tenor_years)
            row_kwargs["fetched_tenors"] = sorted(fetched_tenors)
            output.append(BankOfCanadaYieldsData(**row_kwargs))

        return output
