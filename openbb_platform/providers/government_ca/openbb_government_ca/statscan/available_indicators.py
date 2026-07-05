"""Statistics Canada Available Indicators.

Pure-metadata endpoint: returns the list of available time series
organized by parent-child relationships (cube → series). Carries no
observation values. The catalog is built at install time from the
WDS REST API and stored in the shipped cache.

Supports lookup by vector ID, listing by cube PID or subject, and
free-text search on series labels.
"""

from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.available_indicators import (
    AvailableIndicatorsData,
    AvailableIndicesQueryParams,
)
from pydantic import ConfigDict, Field

from openbb_government_ca.statscan.utils import (
    get_catalog,
    list_cubes,
    lookup_cube,
    lookup_series_by_vector,
    search_series,
)
from openbb_government_ca.utils.metadata import GovernmentCaMetadata


class StatsCanAvailableIndicatorsQueryParams(AvailableIndicesQueryParams):
    """StatsCan Available Indicators Query.

    Supports lookup, list, and search across the SDMX catalog:

    - Pass ``query`` for free-text search on series labels.
    - Pass ``cube_pid`` to list every series in a single cube.
    - Pass ``subject`` to list cubes (and their series) under a subject code.
    - Pass ``vector_id`` to look up a single series by its V-prefixed ID.
    """

    __json_schema_extra__ = {
        "query": {
            "description": (
                "Free-text search on series labels (case-insensitive substring). "
                "e.g. 'GDP', 'unemployment', 'CPI'."
            ),
        },
        "cube_pid": {
            "description": (
                "StatsCan cube Product ID (PID). Lists every series in the cube. "
                "e.g. '10100139' for GDP at basic prices."
            ),
            "multiple_items_allowed": True,
        },
        "subject": {
            "description": (
                "StatsCan subject code. Lists every cube (and its series) under "
                "the subject. Use list_subjects() to see available codes."
            ),
        },
        "vector_id": {
            "description": (
                "StatsCan vector ID (e.g. 'V41886513'). Looks up a single series "
                "and returns it with its parent cube metadata."
            ),
            "multiple_items_allowed": True,
        },
    }

    query: str | None = Field(
        default=None,
        description="Free-text search on series labels.",
    )
    cube_pid: str | None = Field(
        default=None,
        description="Cube Product ID (PID). Comma-separated for multiple.",
    )
    subject: str | None = Field(
        default=None,
        description="StatsCan subject code.",
    )
    vector_id: str | None = Field(
        default=None,
        description="Vector ID (e.g. 'V41886513'). Comma-separated for multiple.",
    )


class StatsCanAvailableIndicatorsData(AvailableIndicatorsData):
    """StatsCan Available Indicators Data."""

    model_config = ConfigDict(extra="ignore")

    __alias_dict__ = {
        "symbol": "vector_id",
        "symbol_root": "label_en",
    }

    cube_pid: str | None = Field(
        default=None,
        description="Parent cube Product ID (PID).",
    )
    cube_title: str | None = Field(
        default=None,
        description="Parent cube title (English).",
    )
    coordinate: str | None = Field(
        default=None,
        description=(
            "StatsCan coordinate string. Combined with the cube PID, "
            "identifies a unique time series."
        ),
    )
    scalar_factor_code: str | None = Field(
        default=None,
        description="Scalar factor code (e.g. '0' = units, '3' = thousands).",
    )
    uom_code: str | None = Field(
        default=None,
        description="Unit of measure code.",
    )


def _series_to_row(series: dict[str, Any], cube: dict[str, Any]) -> dict[str, Any]:
    """Flatten a catalog series + its parent cube into a result row."""
    return {
        "symbol": series.get("vector_id", ""),
        "symbol_root": series.get("label_en", ""),
        "vector_id": series.get("vector_id", ""),
        "cube_pid": cube.get("pid", ""),
        "cube_title": cube.get("title_en", ""),
        "coordinate": series.get("coordinate", ""),
        "description": series.get("label_en", ""),
        "frequency": series.get("frequency_code", ""),
        "scalar_factor_code": series.get("scalar_factor_code", ""),
        "uom_code": series.get("uom_code", ""),
    }


class StatsCanAvailableIndicatorsFetcher(
    Fetcher[
        StatsCanAvailableIndicatorsQueryParams,
        list[StatsCanAvailableIndicatorsData],
    ]
):
    """StatsCan Available Indicators Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> StatsCanAvailableIndicatorsQueryParams:
        """Transform the query."""
        return StatsCanAvailableIndicatorsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: StatsCanAvailableIndicatorsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Search the SDMX catalog. No network calls — pure metadata."""
        meta = GovernmentCaMetadata()
        cache = meta.statscan
        catalog = get_catalog(cache)
        if not catalog or not catalog.get("cubes"):
            return []

        results: list[dict[str, Any]] = []

        if query.vector_id:
            vids = [v.strip() for v in str(query.vector_id).split(",") if v.strip()]
            for vid in vids:
                try:
                    series = lookup_series_by_vector(vid, cache)
                except KeyError:
                    continue
                cube = {
                    "pid": series.get("cube_pid", ""),
                    "title_en": series.get("cube_title_en", ""),
                }
                results.append(_series_to_row(series, cube))
            return results

        if query.cube_pid:
            pids = [p.strip() for p in str(query.cube_pid).split(",") if p.strip()]
            for pid in pids:
                try:
                    cube = lookup_cube(pid, cache)
                except KeyError:
                    continue
                for series in cube.get("series", []):
                    results.append(_series_to_row(series, cube))
            return results

        if query.subject:
            for cube in list_cubes(cache):
                if cube.get("subject_code") == query.subject:
                    for series in cube.get("series", []):
                        results.append(_series_to_row(series, cube))
            return results

        if query.query:
            for series in search_series(query.query, cache):
                cube = {
                    "pid": series.get("cube_pid", ""),
                    "title_en": series.get("cube_title_en", ""),
                }
                results.append(_series_to_row(series, cube))
            return results

        for cube in list_cubes(cache):
            for series in cube.get("series", []):
                results.append(_series_to_row(series, cube))
        return results

    @staticmethod
    def transform_data(
        query: StatsCanAvailableIndicatorsQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[StatsCanAvailableIndicatorsData]:
        """Transform the data."""
        return [StatsCanAvailableIndicatorsData.model_validate(d) for d in data]
