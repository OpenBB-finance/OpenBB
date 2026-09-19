"""ECB Available Indicators Model."""

# pylint: disable=unused-argument

from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.available_indicators import (
    AvailableIndicatorsData,
    AvailableIndicesQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import ConfigDict, Field

_GEOGRAPHY_DIMS = ("REF_AREA", "COUNT_AREA", "CURRENCY")


class ECBAvailableIndicatorsQueryParams(AvailableIndicesQueryParams):
    """ECB Available Indicators Query."""

    __json_schema_extra__ = {
        "dataflow": {
            "x-widget_config": {
                "type": "endpoint",
                "optionsEndpoint": "/api/v1/ecb/list_dataflows",
                "multiSelect": False,
                "style": {"popupWidth": 600},
            },
        },
        "frequency": {
            "x-widget_config": {
                "type": "endpoint",
                "optionsEndpoint": "/api/v1/ecb/indicator_frequencies",
                "optionsParams": {"dataflow": "$dataflow"},
            },
        },
        "reference_area": {
            "x-widget_config": {
                "type": "endpoint",
                "optionsEndpoint": "/api/v1/ecb/indicator_areas",
                "optionsParams": {"dataflow": "$dataflow"},
                "style": {"popupWidth": 500},
            },
        },
        "dimension_values": {
            "multiple_items_allowed": True,
            "x-widget_config": {
                "label": "Other Dimensions",
                "type": "text",
                "multiple": True,
                "value": None,
                "description": "Additional 'DIM:VALUE' filters for the dataflow's"
                " other dimensions — see the ECB Dataflow Dimensions widget for the"
                " ids and codes, e.g. 'ICP_ITEM:000000'.",
            },
        },
    }

    dataflow: str | None = Field(
        default=None,
        description="The ECB dataflow whose series (indicators) to enumerate, e.g."
        " 'ICP'. Use `list_dataflows` / `search_dataflows` to find one.",
    )
    frequency: str | None = Field(
        default=None,
        description="Observation frequency code to narrow to (e.g. 'M').",
    )
    reference_area: str | None = Field(
        default=None,
        description="Reference area / currency code to narrow to (e.g. 'U2').",
    )
    dimension_values: str | list[str] | None = Field(
        default=None,
        description="Additional 'DIM:VALUE' filters for dataflow-specific dimensions"
        " (e.g. 'ICP_ITEM:000000'), beyond frequency / reference area.",
    )
    query: str | None = Field(
        default=None,
        description="Filter series by text in the indicator name."
        " Supports '+' (AND), '|' (OR), and \"quoted phrases\".",
    )
    limit: int | None = Field(
        default=500,
        description="Maximum number of series to return (None or <=0 returns all).",
    )
    use_cache: bool = Field(
        default=True,
        description="Use the parsed-data disk cache for the enumerated series.",
    )
    symbol: str | None = Field(
        default=None,
        exclude=True,
        description="Dummy field so a clicked series can group by symbol.",
    )


class ECBAvailableIndicatorsData(AvailableIndicatorsData):
    """ECB Available Indicators Data."""

    model_config = ConfigDict(
        extra="allow",
        json_schema_extra={
            "symbol": {
                "x-widget_config": {
                    "renderFn": "cellOnClick",
                    "renderFnParams": {
                        "actionType": "groupBy",
                        "groupByParamName": "symbol",
                    },
                }
            }
        },
    )

    dataflow_id: str | None = Field(
        default=None, description="The ECB dataflow the series belongs to."
    )
    series_key: str | None = Field(
        default=None,
        description="The SDMX series key (the dot-joined dimension codes).",
    )


class ECBAvailableIndicatorsFetcher(
    Fetcher[ECBAvailableIndicatorsQueryParams, list[ECBAvailableIndicatorsData]]
):
    """Enumerate the ECB series within a dataflow."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> ECBAvailableIndicatorsQueryParams:
        """Transform query."""
        return ECBAvailableIndicatorsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: ECBAvailableIndicatorsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Enumerate the existing series for the requested dataflow slice."""
        # pylint: disable=import-outside-toplevel
        from openbb_ecb.utils.data_cache import cached_records, make_key
        from openbb_ecb.utils.metadata import EcbMetadata
        from openbb_ecb.utils.metadata._helpers import matches_query, parse_search_query
        from openbb_ecb.utils.query_builder import fetch_series_keys

        metadata = EcbMetadata()
        dataflow = query.dataflow
        if not dataflow or dataflow not in metadata.dataflows:
            raise OpenBBError(
                EmptyDataError(
                    "Provide a valid `dataflow` to enumerate its series (indicators)."
                    " Use `list_dataflows` or `search_dataflows` to find one."
                )
            )

        dimensions = metadata.get_dataflow_dimensions(dataflow)
        chosen: dict[str, str] = {}
        if query.frequency:
            chosen["FREQ"] = query.frequency
        if query.reference_area:
            geography = next(
                (d["id"] for d in dimensions if d["id"] in _GEOGRAPHY_DIMS), None
            )
            if geography:
                chosen[geography] = query.reference_area
        raw_values = query.dimension_values or []
        if isinstance(raw_values, str):
            raw_values = [raw_values]
        for item in raw_values:
            for raw_entry in str(item).split(","):
                entry = raw_entry.strip()
                if entry and ":" in entry:
                    dim_id, value = entry.split(":", 1)
                    chosen[dim_id.strip()] = value.strip()
        key = ".".join(chosen.get(dim["id"], "") for dim in dimensions)

        async def loader() -> list[dict]:
            return await fetch_series_keys(dataflow, key)

        cache_key = make_key("series", flow=dataflow, key=key)
        records = await cached_records(
            "series", cache_key, loader, use_cache=query.use_cache
        )

        if query.query:
            parsed = parse_search_query(query.query)
            records = [r for r in records if matches_query(r.get("name", ""), parsed)]

        if not records:
            raise OpenBBError(
                EmptyDataError(f"No series found for dataflow '{dataflow}'.")
            )

        limit = query.limit
        capped = records[:limit] if limit and limit > 0 else records
        return [{**record, "_dataflow": dataflow} for record in capped]

    @staticmethod
    def transform_data(
        query: ECBAvailableIndicatorsQueryParams, data: list[dict], **kwargs: Any
    ) -> list[ECBAvailableIndicatorsData]:
        """Standardize each enumerated series into an indicator row."""
        results: list[ECBAvailableIndicatorsData] = []
        for record in data:
            dataflow = record.get("_dataflow")
            series_key = record.get("series_key", "")
            results.append(
                ECBAvailableIndicatorsData.model_validate(
                    {
                        "symbol": f"{dataflow}::{series_key}",
                        "symbol_root": dataflow,
                        "dataflow_id": dataflow,
                        "series_key": series_key,
                        "description": record.get("name"),
                        "frequency": record.get("FREQ__label") or record.get("FREQ"),
                        "country": record.get("REF_AREA__label"),
                    }
                )
            )
        return results
