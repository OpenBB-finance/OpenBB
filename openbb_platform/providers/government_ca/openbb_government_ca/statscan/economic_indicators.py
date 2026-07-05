"""Statistics Canada Economic Indicators.

Fetches time-series observations from the StatsCan WDS REST API.
Supports two addressing modes:

- **Single series** — pass one or more vector IDs (e.g. ``V41886513``).
  The fetcher calls ``getDataFromVectorByReferencePeriodRange`` for
  each vector and concatenates the results.
- **Full hierarchical table** — pass a cube PID (e.g. ``10100139``).
  The fetcher calls ``getFullTableDownloadSDMX`` and returns every
  series in the cube.

Maps to OpenBB's standard ``economy.indicators`` model — the same
model used by ``openbb-oecd``.

The metadata cache is used only to resolve parameters (validate the
vector ID exists, look up its cube PID, derive its frequency for the
diskcache TTL). The observation values themselves are never read from
the cache — they always come from the WDS API (or the diskcache layer
in front of it).
"""

from datetime import date, timedelta
from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.economic_indicators import (
    EconomicIndicatorsData,
    EconomicIndicatorsQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

from openbb_government_ca.statscan._client import StatsCanClient
from openbb_government_ca.statscan.utils import (
    get_catalog,
    lookup_cube,
    lookup_series_by_vector,
)
from openbb_government_ca.utils.helpers import parse_observation_date, safe_float
from openbb_government_ca.utils.metadata import GovernmentCaMetadata


def _default_start_date() -> date:
    """Return 1 year ago as a default start_date."""
    return date.today() - timedelta(days=365)


class StatsCanEconomicIndicatorsQueryParams(EconomicIndicatorsQueryParams):
    """StatsCan Economic Indicators Query.

    The ``symbol`` field accepts:

    - A vector ID (``"V41886513"``) — fetches a single time series.
    - A comma-separated list of vector IDs.
    - A cube PID prefixed with ``cube:`` (``"cube:10100139"``) —
      fetches every series in the cube as a hierarchical table.
    - The special token ``"homepage"`` — fetches the curated list of
      "key economic indicators" from the StatsCan homepage.
    """

    __json_schema_extra__ = {
        "symbol": {
            "multiple_items_allowed": True,
            "description": (
                "Vector ID (e.g. 'V41886513'), comma-separated list of "
                "vector IDs, 'cube:PID' to fetch a full hierarchical table, "
                "or 'homepage' for the curated key-economic-indicators list."
            ),
        },
        "country": {
            "description": (
                "Optional geo code filter. StatsCan geo codes: '0' = Canada, "
                "'1' = Newfoundland and Labrador, '13' = Nunavut, etc. "
                "Leave empty to include all geographies."
            ),
        },
    }

    country: str | None = Field(
        default=None,
        description="Optional StatsCan geo_code filter (e.g. '0' for Canada).",
    )
    start_date: date | None = Field(
        default=None,
        description="Start date (YYYY-MM-DD). Defaults to 1 year ago.",
    )
    end_date: date | None = Field(
        default=None,
        description="End date (YYYY-MM-DD). Defaults to today.",
    )


class StatsCanEconomicIndicatorsData(EconomicIndicatorsData):
    """StatsCan Economic Indicators Data."""

    vector_id: str | None = Field(
        default=None,
        description="StatsCan vector ID for this observation.",
    )
    cube_pid: str | None = Field(
        default=None,
        description="Parent cube Product ID (PID).",
    )
    coordinate: str | None = Field(
        default=None,
        description="StatsCan coordinate string (uniquely identifies the series within the cube).",
    )
    scalar_factor_code: str | None = Field(
        default=None,
        description="Scalar factor code applied to the value.",
    )
    uom_code: str | None = Field(
        default=None,
        description="Unit-of-measure code.",
    )
    refper_raw: str | None = Field(
        default=None,
        description="Raw reference period string from StatsCan (e.g. '2024-01').",
    )


class StatsCanEconomicIndicatorsFetcher(
    Fetcher[
        StatsCanEconomicIndicatorsQueryParams,
        list[StatsCanEconomicIndicatorsData],
    ]
):
    """StatsCan Economic Indicators Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> StatsCanEconomicIndicatorsQueryParams:
        """Transform the raw params dict into a validated query model."""
        transformed = params.copy()
        if not transformed.get("symbol"):
            transformed["symbol"] = "homepage"
        country = transformed.get("country")
        if country and isinstance(country, str):
            lower = country.lower().strip()
            if lower in {"canada", "ca", "can"}:
                transformed["country"] = "0"
        if transformed.get("start_date") is None:
            transformed["start_date"] = _default_start_date()
        if transformed.get("end_date") is None:
            transformed["end_date"] = date.today()
        return StatsCanEconomicIndicatorsQueryParams(**transformed)

    @staticmethod
    def _resolve_homepage_vectors(cache: dict[str, Any]) -> list[str]:
        """Return the vector IDs from the homepage indicators list."""
        indicators = cache.get("indicators", [])
        vectors: list[str] = []
        for ind in indicators:
            source = str(ind.get("source", "")).strip()
            if source:
                vectors.append(source if source.startswith("V") else f"V{source}")
        return vectors

    @staticmethod
    def _fetch_vectors(
        client: StatsCanClient,
        vector_ids: list[str],
        start_date: date,
        end_date: date,
        cache: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """Fetch observations for each vector ID in *vector_ids*.

        Each observation is enriched with its parent cube's PID, the
        vector ID, and the series' frequency code (used by the diskcache
        layer to set a TTL).
        """
        start_ref = start_date.strftime("%Y-%m")
        end_ref = end_date.strftime("%Y-%m")
        all_observations: list[dict[str, Any]] = []

        for vid in vector_ids:
            try:
                series_meta = lookup_series_by_vector(vid, cache)
            except KeyError:
                continue
            frequency_code = series_meta.get("frequency_code")
            payload = client.get_data_from_vector_by_reference_period_range(
                vid,
                start_ref,
                end_ref,
                frequency_code=frequency_code,
            )
            for spot in payload:
                if not isinstance(spot, dict):
                    continue
                enriched = dict(spot)
                enriched["_vector_id"] = vid
                enriched["_cube_pid"] = series_meta.get("cube_pid", "")
                enriched["_coordinate"] = series_meta.get("coordinate", "")
                enriched["_scalar_factor_code"] = series_meta.get(
                    "scalar_factor_code", ""
                )
                enriched["_uom_code"] = series_meta.get("uom_code", "")
                enriched["_label_en"] = series_meta.get("label_en", "")
                all_observations.append(enriched)
        return all_observations

    @staticmethod
    def _fetch_cube(
        client: StatsCanClient,
        pid: str,
        cache: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """Fetch every series in a cube as a hierarchical table.

        Iterates the cube's catalog series list and fetches each one
        by vector ID. Returns enriched observations.
        """
        try:
            cube = lookup_cube(pid, cache)
        except KeyError as exc:
            raise OpenBBError(str(exc)) from exc

        series_list = cube.get("series", [])
        if not series_list:
            raise EmptyDataError(f"StatsCan cube {pid!r} has no series in the catalog.")

        today = date.today()
        start_ref = (today - timedelta(days=365 * 5)).strftime("%Y-%m")
        end_ref = today.strftime("%Y-%m")

        all_observations: list[dict[str, Any]] = []
        for series in series_list:
            vid = str(series.get("vector_id", ""))
            if not vid:
                continue
            frequency_code = series.get("frequency_code")
            try:
                payload = client.get_data_from_vector_by_reference_period_range(
                    vid,
                    start_ref,
                    end_ref,
                    frequency_code=frequency_code,
                )
            except Exception:  # noqa: BLE001, S112
                continue
            for spot in payload:
                if not isinstance(spot, dict):
                    continue
                enriched = dict(spot)
                enriched["_vector_id"] = vid
                enriched["_cube_pid"] = pid
                enriched["_coordinate"] = series.get("coordinate", "")
                enriched["_scalar_factor_code"] = series.get("scalar_factor_code", "")
                enriched["_uom_code"] = series.get("uom_code", "")
                enriched["_label_en"] = series.get("label_en", "")
                all_observations.append(enriched)
        return all_observations

    @staticmethod
    def extract_data(
        query: StatsCanEconomicIndicatorsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Fetch observations from the StatsCan WDS REST API."""
        meta = GovernmentCaMetadata()
        cache = meta.statscan
        catalog = get_catalog(cache)
        if not catalog or not catalog.get("cubes"):
            raise OpenBBError(
                "StatsCan SDMX catalog is empty or in degraded mode — the "
                "package was built when www150.statcan.gc.ca was unreachable. "
                "Reinstall openbb-government-ca with "
                "OPENBB_GOVERNMENT_CA_FORCE_CACHE_REBUILD=1 to retry."
            )

        client = StatsCanClient()

        symbol = str(query.symbol).strip()
        assert query.start_date is not None  # noqa: S101
        assert query.end_date is not None  # noqa: S101

        if symbol.lower() == "homepage":
            vectors = StatsCanEconomicIndicatorsFetcher._resolve_homepage_vectors(cache)
            if not vectors:
                raise EmptyDataError(
                    "StatsCan homepage indicators list is empty. The cache "
                    "may be in degraded mode — reinstall the package."
                )
            observations = StatsCanEconomicIndicatorsFetcher._fetch_vectors(
                client,
                vectors,
                query.start_date,
                query.end_date,
                cache,
            )
        elif symbol.lower().startswith("cube:"):
            pid = symbol.split(":", 1)[1].strip()
            observations = StatsCanEconomicIndicatorsFetcher._fetch_cube(
                client, pid, cache
            )
        else:
            vector_ids = [v.strip() for v in symbol.split(",") if v.strip()]
            if not vector_ids:
                raise EmptyDataError(
                    "No vector IDs parsed from symbol. Pass a vector ID "
                    "(e.g. 'V41886513'), 'cube:PID', or 'homepage'."
                )
            observations = StatsCanEconomicIndicatorsFetcher._fetch_vectors(
                client,
                vector_ids,
                query.start_date,
                query.end_date,
                cache,
            )

        if not observations:
            raise EmptyDataError(
                f"StatsCan returned no observations for symbol={query.symbol!r} "
                f"in the range {query.start_date} to {query.end_date}."
            )

        if query.country:
            observations = [
                obs
                for obs in observations
                if str(obs.get("_geo_code", "")) == str(query.country)
                or (not obs.get("_geo_code") and str(query.country) == "0")
            ]
            if not observations:
                raise EmptyDataError(
                    f"No observations matched country filter {query.country!r}."
                )

        return observations

    @staticmethod
    def transform_data(
        query: StatsCanEconomicIndicatorsQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[StatsCanEconomicIndicatorsData]:
        """Map raw WDS observations to the standard ``EconomicIndicatorsData`` model.

        Each WDS observation has the shape::

            {
                "refPer": "2024-01",
                "value": 47.6,
                "scalarFactorCode": "6",
                "decimals": 1,
                "releaseTime": "2024-03-01",
            }

        Values are returned as-is (no scaling); the ``scalar_factor_code``
        and ``uom_code`` extension fields let callers apply scale if
        needed.
        """
        output: list[StatsCanEconomicIndicatorsData] = []
        for spot in data:
            refper_raw = str(spot.get("refPer", "")) or str(spot.get("refperRaw", ""))
            obs_date = parse_observation_date(refper_raw)
            value = safe_float(spot.get("value"))
            label_en = str(spot.get("_label_en", ""))

            output.append(
                StatsCanEconomicIndicatorsData(
                    date=obs_date,
                    symbol_root=label_en or None,
                    symbol=str(spot.get("_vector_id", "")) or None,
                    country="Canada",
                    value=value,
                    vector_id=str(spot.get("_vector_id", "")) or None,
                    cube_pid=str(spot.get("_cube_pid", "")) or None,
                    coordinate=str(spot.get("_coordinate", "")) or None,
                    scalar_factor_code=str(spot.get("_scalar_factor_code", "")) or None,
                    uom_code=str(spot.get("_uom_code", "")) or None,
                    refper_raw=refper_raw or None,
                )
            )

        output.sort(
            key=lambda x: (
                x.symbol or "",
                x.date is None,
                -(x.date.toordinal() if x.date else 0),
            )
        )
        return output
