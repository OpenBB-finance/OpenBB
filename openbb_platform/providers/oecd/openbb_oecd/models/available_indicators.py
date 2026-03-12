"""OECD Available Indicators Model."""

# pylint: disable=unused-argument

from typing import Any

from openbb_core.app.service.system_service import SystemService
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.available_indicators import (
    AvailableIndicatorsData,
    AvailableIndicesQueryParams,
)
from pydantic import ConfigDict, Field

api_prefix = SystemService().system_settings.api_settings.prefix


def _build_also_in(
    indicator: str,
    df_id: str,
    code_to_dataflows: dict[str, list[str]],
    df_name_cache: dict[str, str],
    metadata,
) -> list[str]:
    """Build 'also_in' cross-reference list from pre-built reverse index."""
    if not indicator or indicator not in code_to_dataflows:
        return []

    # Deduplicate while preserving order.
    seen: set[str] = set()
    unique: list[str] = []
    for d in code_to_dataflows[indicator]:
        if d != df_id and d not in seen:
            seen.add(d)
            unique.append(d)

    labeled: list[str] = []
    for other_id in unique[:10]:
        name = df_name_cache.get(other_id, "")
        if not name:
            try:
                full_id = metadata._resolve_dataflow_id(  # noqa: SLF001  # pylint: disable=W0212
                    other_id
                )
                name = df_name_cache.get(full_id, "")
            except Exception:  # noqa: BLE001, S110
                pass
        labeled.append(f"{other_id} ({name})" if name else other_id)
    if len(unique) > 10:
        labeled.append(f"... and {len(unique) - 10} more")
    return labeled


class OecdAvailableIndicatorsQueryParams(AvailableIndicesQueryParams):
    """OECD Available Indicators Query.

    Search the OECD SDMX catalogue for indicators across all dataflows.
    Supports AND/OR/quoted-phrase queries and dataflow filtering.
    """

    __json_schema_extra__ = {
        "topic": {
            "x-widget_config": {
                "label": "Topic",
                "description": "Filter by topic. Leave blank for all topics.",
                "type": "endpoint",
                "optionsEndpoint": f"{api_prefix}/oecd_utils/list_topic_choices",
                "style": {"popupWidth": 600},
                "optional": True,
            },
        },
        "dataflow": {
            "multiple_items_allowed": True,
            "x-widget_config": {
                "label": "Dataflow",
                "description": "Filter to specific dataflow(s). Leave blank for all.",
                "type": "endpoint",
                "multiSelect": True,
                "multiple": False,
                "optionsEndpoint": f"{api_prefix}/oecd_utils/list_dataflow_choices",
                "style": {"popupWidth": 700},
                "optional": True,
            },
        },
    }
    topic: str | None = Field(
        default=None,
        description="Filter to a topic ID (e.g. 'ECO', 'HEA'). Use list_topics() to see available topics.",
    )
    dataflows: str | list[str] | None = Field(
        default=None,
        description="Filter by dataflow ID(s). Comma-separated or list. e.g. 'DF_KEI' or 'DF_KEI,DF_QNA'.",
    )
    query: str | None = Field(
        default=None,
        description=(
            "Search string. Use quotes for exact phrases, + for AND, | for OR. "
            "e.g. 'GDP growth', 'CPI | inflation', 'balance +trade'."
        ),
    )
    keywords: str | list[str] | None = Field(
        default=None,
        description="Single-word keyword filter(s). Prefix with 'not' to exclude.",
    )


class OecdAvailableIndicatorsData(AvailableIndicatorsData):
    """OECD Available Indicators Data."""

    model_config = ConfigDict(extra="ignore")

    __alias_dict__ = {
        "symbol": "series_id",
        "symbol_root": "indicator",
    }

    label: str | None = Field(
        default=None, description="Short human-readable name of the indicator."
    )
    dataflow_id: str = Field(description="Dataflow identifier.")
    dataflow_name: str | None = Field(
        default=None, description="Human-readable dataflow name."
    )
    dimension_id: str | None = Field(
        default=None, description="Dimension containing the indicator."
    )
    parent: str | None = Field(
        default=None, description="Parent indicator code in the codelist hierarchy."
    )
    frequencies: list[str] = Field(
        default_factory=list,
        description="Available observation frequencies (e.g. Annual, Quarterly, Monthly).",
    )
    transformations: list[str] = Field(
        default_factory=list,
        description="Available data transformations (e.g. Growth rate, Index).",
    )
    member_of: list[str] = Field(
        default_factory=list,
        description="Presentation tables containing this indicator (e.g. 'DF_EO::T101').",
    )
    also_in: list[str] = Field(
        default_factory=list,
        description="Other OECD tables that also contain this indicator code.",
    )


class OecdAvailableIndicatorsFetcher(
    Fetcher[OecdAvailableIndicatorsQueryParams, list[OecdAvailableIndicatorsData]]
):
    """OECD Available Indicators Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> OecdAvailableIndicatorsQueryParams:
        """Transform the query."""
        return OecdAvailableIndicatorsQueryParams(**params)

    @staticmethod
    def _build_enrichment_indexes(metadata):  # noqa: PLR0912
        """Build reverse indexes from the in-memory cache for fast enrichment.

        Returns code_to_dataflows, indicator_to_tables, constrained_cache,
        df_name_cache — all derived from already-loaded data with NO API calls.
        """
        # Reverse index: indicator_code → list of short dataflow IDs.
        code_to_dataflows: dict[str, list[str]] = {}
        for (
            _full_id,
            inds,
        ) in (
            metadata._dataflow_indicators_cache.items()  # noqa: SLF001  # pylint: disable=W0212
        ):
            for ind in inds:
                code = ind.get("indicator", "")
                if code:
                    code_to_dataflows.setdefault(code, []).append(
                        ind.get("dataflow_id", _full_id)
                    )

        # Dataflow name lookup.
        df_name_cache: dict[str, str] = {}
        for fid, meta_entry in metadata.dataflows.items():
            short = meta_entry.get("short_id", "")
            name = meta_entry.get("name", "")
            if short:
                df_name_cache[short] = name
            df_name_cache[fid] = name

        return code_to_dataflows, df_name_cache

    @staticmethod
    def _enrich_results(  # noqa: PLR0912
        results: list[dict],
        metadata,
        code_to_dataflows: dict[str, list[str]],
        df_name_cache: dict[str, str],
    ) -> list[dict]:
        """Enrich search results with symbol, membership, and cross-refs.

        Uses only pre-built indexes and already-cached structures.
        """
        # Pre-fetch constrained values for all target dataflows (batch).
        # ONLY use dataflows whose structures AND parameters are already cached.
        target_dfs = {r.get("dataflow_id", "") for r in results} - {""}
        constrained_cache: dict[str, dict] = {}

        for df_id in target_dfs:
            full_id = metadata._short_id_map.get(  # noqa: SLF001 # pylint: disable=W0212
                df_id
            )
            if not full_id:
                full_id = df_id if df_id in metadata.datastructures else None
            if not full_id or full_id not in metadata.datastructures:
                continue
            if (
                full_id not in metadata._dataflow_parameters_cache  # noqa: SLF001  # pylint: disable=W0212
            ):
                continue
            try:
                constrained_cache[df_id] = metadata.get_constrained_values(full_id)
            except Exception:  # noqa: BLE001
                constrained_cache[df_id] = {}

        for row in results:
            df_id = row.get("dataflow_id", "")
            indicator = row.get("indicator", "")

            # Clean symbol: DATAFLOW::INDICATOR_CODE.
            row["series_id"] = (
                f"{df_id}::{indicator}" if df_id and indicator else (indicator or df_id)
            )
            row["symbol"] = row["series_id"]

            # Cross-reference: other dataflows containing this indicator.
            row["also_in"] = _build_also_in(
                indicator, df_id, code_to_dataflows, df_name_cache, metadata
            )

            # Frequencies and transformations from pre-fetched constrained values.
            constrained = constrained_cache.get(df_id, {})
            row["frequencies"] = [
                f"{e['value']} ({e['label']})"
                for e in constrained.get("FREQ", [])
                if e.get("value")
            ]
            row["transformations"] = [
                f"{e['value']} ({e['label']})"
                for e in constrained.get("TRANSFORMATION", [])
                if e.get("value")
            ]

            # Table membership placeholder (populated from cache constraints).
            row.setdefault("member_of", [])

        return results

    @staticmethod
    def extract_data(
        query: OecdAvailableIndicatorsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Search OECD indicators using the metadata catalogue."""
        # pylint: disable=import-outside-toplevel
        from openbb_oecd.utils.metadata import OecdMetadata

        metadata = OecdMetadata()
        dataflows = query.dataflows

        if isinstance(dataflows, str):
            dataflows = [d.strip() for d in dataflows.split(",") if d.strip()]

        # If a topic filter is given, expand it to the dataflows in that topic
        # and intersect with any explicit dataflow filter.
        if query.topic:
            topic_dfs = [e["value"] for e in metadata.list_dataflows(topic=query.topic)]
            if dataflows:
                intersected = [
                    d
                    for d in topic_dfs
                    if any(d.endswith(f) or d == f for f in dataflows)
                ]
                dataflows = intersected if intersected else dataflows
            else:
                dataflows = topic_dfs

        keywords = query.keywords

        if isinstance(keywords, str):
            keywords = [k.strip() for k in keywords.split(",") if k.strip()]

        results = metadata.search_indicators(
            query=query.query or "",
            dataflows=dataflows,
            keywords=keywords,
        )

        if not results:
            return results

        # Build reverse indexes ONCE from already-loaded cache (no API calls).
        code_to_dataflows, df_name_cache = (
            OecdAvailableIndicatorsFetcher._build_enrichment_indexes(metadata)
        )

        return OecdAvailableIndicatorsFetcher._enrich_results(
            results, metadata, code_to_dataflows, df_name_cache
        )

    @staticmethod
    def transform_data(
        query: OecdAvailableIndicatorsQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[OecdAvailableIndicatorsData]:
        """Transform the data."""
        return [OecdAvailableIndicatorsData.model_validate(d) for d in data]
