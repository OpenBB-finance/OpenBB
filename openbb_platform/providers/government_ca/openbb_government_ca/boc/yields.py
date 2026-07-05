"""Bank of Canada — Benchmark Government of Canada Bond Yields.

Maps to OpenBB's standard ``treasury_rates`` model. Per the brief:
- ``year_2``, ``year_3``, ``year_5``, ``year_7``, ``year_10``,
  ``year_30`` are populated from the corresponding BoC series.
- All sub-1Y fields and ``year_20`` are left as ``None``.
- Values are normalized to decimals (3.18 → 0.0318) per the model's
  docstring: "1% = 0.01".
"""

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

_TENOR_YEARS_TO_FIELD: dict[int, str] = {
    2: "year_2",
    3: "year_3",
    5: "year_5",
    7: "year_7",
    10: "year_10",
    30: "year_30",
}

_MAX_PARALLEL_FETCH = 6


def _default_start_date() -> date:
    """Return 1 year ago as a default start_date."""
    return date.today() - timedelta(days=365)


class BankOfCanadaYieldsQueryParams(TreasuryRatesQueryParams):
    """BoC Benchmark Bond Yields Query."""

    start_date: date | None = Field(
        default=None,
        description="Start date (YYYY-MM-DD). Defaults to 1 year ago.",
    )
    end_date: date | None = Field(
        default=None,
        description="End date (YYYY-MM-DD). Defaults to today.",
    )


class BankOfCanadaYieldsData(TreasuryRatesData):
    """BoC Benchmark Bond Yields Data."""

    fetched_tenors: list[str] | None = Field(
        default=None,
        description="List of tenor labels actually fetched (e.g. ['2Y', '10Y', 'LONG']).",
    )


class BankOfCanadaYieldsFetcher(
    Fetcher[BankOfCanadaYieldsQueryParams, list[BankOfCanadaYieldsData]]
):
    """BoC Benchmark Bond Yields Fetcher."""

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
        """Return ``{tenor_years: series_entry}`` for every cataloged bond."""
        bond_series: dict[int, dict[str, Any]] = {}
        for entry in list_series(boc_cache):
            tenor_years = entry.get("tenor_years")
            if tenor_years is None:
                continue
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
        """Fetch observations for a single bond series. Returns ``(tenor_years, observations)``."""
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
            return (tenor_years, [])

        observations = (
            payload.get("observations", []) if isinstance(payload, dict) else []
        )
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
        """Fetch observations for all bond tenors in parallel."""
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

        assert query.start_date is not None  # noqa: S101
        assert query.end_date is not None  # noqa: S101

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
        """Pivot flat observations into ``treasury_rates`` rows by date."""
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
            normalized = raw_value / 100.0
            by_date.setdefault(obs_date, {})[int(tenor_years)] = normalized

            for ty, field_name in _TENOR_YEARS_TO_FIELD.items():
                if int(tenor_years) == ty:
                    label = f"{ty}Y" if ty != 30 else "LONG"
                    fetched_tenors.add(label)

        output: list[BankOfCanadaYieldsData] = []
        for obs_date in sorted(by_date.keys()):
            tenor_values = by_date[obs_date]
            row_kwargs: dict[str, Any] = {"date": obs_date}
            for tenor_years, field_name in _TENOR_YEARS_TO_FIELD.items():
                row_kwargs[field_name] = tenor_values.get(tenor_years)
            row_kwargs["fetched_tenors"] = sorted(fetched_tenors)
            output.append(BankOfCanadaYieldsData(**row_kwargs))

        return output
