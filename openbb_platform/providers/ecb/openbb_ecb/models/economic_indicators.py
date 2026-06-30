"""ECB Economic Indicators Model.

Fetch any ECB SDMX series by a ``FLOW::KEY`` symbol, e.g.
``EXR::D.USD.EUR.SP00.A`` or ``BSI::M.U2.Y.V.M30.X.1.U2.2300.Z01.E``. The key
is the dot-joined dimension key; ``+`` is OR and an empty segment is a wildcard.
"""

# pylint: disable=unused-argument

from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.economic_indicators import (
    EconomicIndicatorsData,
    EconomicIndicatorsQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import ConfigDict, Field

_FREQ_DIMS = {"FREQ", "FREQUENCY"}
_AREA_DIMS = {"REF_AREA", "AREA", "COUNTERPART_AREA", "COUNTRY"}


class ECBEconomicIndicatorsQueryParams(EconomicIndicatorsQueryParams):
    """ECB Economic Indicators Query."""

    __json_schema_extra__ = {"symbol": {"multiple_items_allowed": True}}

    use_cache: bool = Field(
        default=True,
        description="If true, cache parsed results on disk for the dataset TTL.",
    )


class ECBEconomicIndicatorsData(EconomicIndicatorsData):
    """ECB Economic Indicators Data."""

    model_config = ConfigDict(extra="allow")

    title: str | None = Field(default=None, description="Descriptive series title.")
    frequency: str | None = Field(default=None, description="The series frequency.")
    unit: str | None = Field(default=None, description="The unit of the observation.")


def _build_title(record: dict) -> str:
    """Compose a readable title from a record's dimension labels (not attributes)."""
    parts = []
    for dim in record.get("_dim_ids", []):
        if dim in _FREQ_DIMS:
            continue
        label = record.get(f"{dim}__label")
        if label:
            parts.append(str(label))
    return " - ".join(dict.fromkeys(parts))


class ECBEconomicIndicatorsFetcher(
    Fetcher[ECBEconomicIndicatorsQueryParams, list[ECBEconomicIndicatorsData]]
):
    """Fetch ECB series by ``FLOW::KEY`` symbol."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> ECBEconomicIndicatorsQueryParams:
        """Transform query."""
        return ECBEconomicIndicatorsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: ECBEconomicIndicatorsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Fetch each symbol's series, with disk caching per symbol."""
        # pylint: disable=import-outside-toplevel
        import asyncio

        from openbb_ecb.utils.data_cache import cached_records, make_key
        from openbb_ecb.utils.metadata import EcbMetadata
        from openbb_ecb.utils.query_builder import fetch_sdmx_data

        metadata = EcbMetadata()
        symbols = [s.strip() for s in str(query.symbol).split(",") if s.strip()]
        start = query.start_date.strftime("%Y-%m-%d") if query.start_date else None
        end = query.end_date.strftime("%Y-%m-%d") if query.end_date else None

        async def get_one(symbol: str) -> list[dict]:
            if "::" not in symbol:
                raise OpenBBError(
                    f"Invalid ECB symbol '{symbol}'. Use 'FLOW::KEY', e.g. "
                    "'EXR::D.USD.EUR.SP00.A'."
                )
            flow, key = symbol.split("::", 1)
            if flow not in metadata.dataflows:
                raise OpenBBError(
                    f"Unknown ECB dataflow '{flow}'. Use `available_indicators` "
                    "to search the catalogue."
                )

            async def loader() -> list[dict]:
                return await fetch_sdmx_data(
                    flow, key, start_date=start, end_date=end, raise_empty=False
                )

            cache_key = make_key("indicators", symbol=symbol, start=start, end=end)
            records = await cached_records(
                "indicators", cache_key, loader, use_cache=query.use_cache
            )
            for record in records:
                record["_flow"] = flow
                record["_symbol_in"] = symbol
            return records

        gathered = await asyncio.gather(*[get_one(s) for s in symbols])
        results = [record for batch in gathered for record in batch]
        if not results:
            raise OpenBBError(
                EmptyDataError("No data found for the requested symbol(s).")
            )
        return results

    @staticmethod
    def transform_data(
        query: ECBEconomicIndicatorsQueryParams, data: list[dict], **kwargs: Any
    ) -> list[ECBEconomicIndicatorsData]:
        """Standardize records into the model."""
        results: list[ECBEconomicIndicatorsData] = []
        for record in data:
            flow = record.get("_flow", "")
            country = None
            for area in _AREA_DIMS:
                if record.get(f"{area}__label"):
                    country = record[f"{area}__label"]
                    break
            frequency = next(
                (
                    record.get(f"{d}__label")
                    for d in _FREQ_DIMS
                    if record.get(f"{d}__label")
                ),
                None,
            )
            row = {
                "date": record.get("date"),
                "symbol_root": flow,
                "symbol": f"{flow}::{record.get('series_key', '')}",
                "country": country,
                "value": record.get("OBS_VALUE"),
                "title": _build_title(record) or None,
                "frequency": frequency,
                "unit": record.get("UNIT") or record.get("UNIT_MEASURE"),
            }
            results.append(ECBEconomicIndicatorsData.model_validate(row))
        results.sort(key=lambda r: (r.symbol or "", str(r.date)))
        return results
