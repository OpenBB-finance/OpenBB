"""Bank of Canada — Policy Overnight Rate Target.

Maps to OpenBB's standard ``country_interest_rates`` model. The value
is normalized to a decimal (5.00 → 0.05) per the model's
``x-frontend_multiply: 100`` directive, matching the OECD fetcher
pattern.
"""

from datetime import date, timedelta
from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.country_interest_rates import (
    CountryInterestRatesData,
    CountryInterestRatesQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

from openbb_government_ca.boc.utils import (
    is_degraded,
    lookup_series,
    lookup_series_by_description,
)
from openbb_government_ca.utils._http import NetworkError, http_get_json
from openbb_government_ca.utils.metadata import GovernmentCaMetadata

_TARGET_RATE_DESCRIPTION = "Target for the overnight rate"
_PREFERRED_SERIES_NAMES = ("CBC20210", "V39079")


def _default_start_date() -> date:
    """Return 1 year ago as a default start_date."""
    return date.today() - timedelta(days=365)


class BankOfCanadaRatesQueryParams(CountryInterestRatesQueryParams):
    """BoC Policy Rate Query."""

    __json_schema_extra__ = {
        "country": {
            "description": (
                "Locked to 'canada' — this fetcher only returns the BoC "
                "policy overnight rate target."
            ),
            "choices": ["canada"],
        },
    }

    country: str = Field(
        default="canada",
        description="The country (always 'canada' for this fetcher).",
    )
    start_date: date | None = Field(
        default=None,
        description="Start date (YYYY-MM-DD). Defaults to 1 year ago.",
    )
    end_date: date | None = Field(
        default=None,
        description="End date (YYYY-MM-DD). Defaults to today.",
    )


class BankOfCanadaRatesData(CountryInterestRatesData):
    """BoC Policy Rate Data."""

    series: str | None = Field(
        default=None,
        description="The BoC Valet series name (e.g. 'CBC20210' or 'V39079').",
    )


class BankOfCanadaRatesFetcher(
    Fetcher[BankOfCanadaRatesQueryParams, list[BankOfCanadaRatesData]]
):
    """BoC Policy Overnight Rate Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> BankOfCanadaRatesQueryParams:
        """Transform raw params into a validated query model."""
        transformed = params.copy()
        transformed["country"] = "canada"
        if transformed.get("start_date") is None:
            transformed["start_date"] = _default_start_date()
        if transformed.get("end_date") is None:
            transformed["end_date"] = date.today()
        return BankOfCanadaRatesQueryParams(**transformed)

    @staticmethod
    def _resolve_target_series(boc_cache: dict) -> dict[str, Any] | None:
        """Find the target rate series in the cache, preferring CBC20210."""
        matches = lookup_series_by_description(_TARGET_RATE_DESCRIPTION, boc_cache)
        if not matches:
            return None

        for preferred in _PREFERRED_SERIES_NAMES:
            for m in matches:
                if m.get("name") == preferred:
                    return m

        return matches[0]

    @staticmethod
    def extract_data(
        query: BankOfCanadaRatesQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Fetch observations from the BoC Valet API."""
        meta = GovernmentCaMetadata()
        boc_cache = meta.boc

        if is_degraded(boc_cache):
            raise OpenBBError(
                "Bank of Canada metadata cache is in degraded mode — the "
                "package was built when www.bankofcanada.ca was unreachable. "
                "Reinstall openbb-government-ca with "
                "OPENBB_GOVERNMENT_CA_FORCE_CACHE_REBUILD=1 to retry."
            )

        entry = BankOfCanadaRatesFetcher._resolve_target_series(boc_cache)
        if entry is None:
            for name in _PREFERRED_SERIES_NAMES:
                try:
                    entry = lookup_series(name, boc_cache)
                    break
                except KeyError:
                    continue

        if entry is None:
            raise OpenBBError(
                "Could not find the BoC target overnight rate series in the "
                "cache. Looked for any series with description containing "
                f"{_TARGET_RATE_DESCRIPTION!r}, and direct lookups for "
                f"{_PREFERRED_SERIES_NAMES}. The cache may be incomplete."
            )

        series_name = str(entry.get("name", ""))
        observations_url = entry.get("observations_url", "")
        if not observations_url:
            raise OpenBBError(
                f"BoC series {series_name!r} has no observations_url in the cache."
            )

        assert query.start_date is not None  # noqa: S101
        assert query.end_date is not None  # noqa: S101
        params: dict[str, str] = {
            "start_date": query.start_date.strftime("%Y-%m-%d"),
            "end_date": query.end_date.strftime("%Y-%m-%d"),
        }

        try:
            payload = http_get_json(observations_url, params=params, timeout=30.0)
        except NetworkError as exc:
            raise OpenBBError(
                f"Failed to fetch BoC observations for {series_name!r} "
                f"from {observations_url}: {exc}"
            ) from exc

        observations = (
            payload.get("observations", []) if isinstance(payload, dict) else []
        )
        if not observations:
            raise EmptyDataError(
                f"BoC returned no observations for {series_name!r} in the "
                f"date range {query.start_date} to {query.end_date}."
            )

        for obs in observations:
            obs["_series"] = series_name

        return observations

    @staticmethod
    def transform_data(
        query: BankOfCanadaRatesQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[BankOfCanadaRatesData]:
        """Map raw Valet observations to the standard ``CountryInterestRatesData`` model."""
        output: list[BankOfCanadaRatesData] = []
        for obs in data:
            obs_date_str = obs.get("d")
            if not obs_date_str:
                continue
            try:
                obs_date = date.fromisoformat(str(obs_date_str))
            except ValueError:
                continue

            series_name = str(obs.get("_series", ""))
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

            normalized_value = raw_value / 100.0

            output.append(
                BankOfCanadaRatesData(
                    date=obs_date,
                    value=normalized_value,
                    country="canada",
                    series=series_name or None,
                )
            )

        output.sort(key=lambda x: x.date)
        return output
