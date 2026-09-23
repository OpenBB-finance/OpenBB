"""ECB Euro Short-Term Rate Model."""

# pylint: disable=unused-argument

from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.euro_short_term_rate import (
    EuroShortTermRateData,
    EuroShortTermRateQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

_PERCENT_FIELDS = {
    "rate",
    "percentile_25",
    "percentile_75",
    "large_bank_share_of_volume",
}
_INT_FIELDS = {"transactions", "number_of_banks"}


class ECBEuroShortTermRateQueryParams(EuroShortTermRateQueryParams):
    """ECB Euro Short-Term Rate Query."""

    use_cache: bool = Field(
        default=True,
        description="If true, cache parsed results on disk for the dataset TTL.",
    )


class ECBEuroShortTermRateData(EuroShortTermRateData):
    """ECB Euro Short-Term Rate Data."""


class ECBEuroShortTermRateFetcher(
    Fetcher[ECBEuroShortTermRateQueryParams, list[ECBEuroShortTermRateData]]
):
    """Fetch the €STR and its detail from the ECB EST dataflow."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> ECBEuroShortTermRateQueryParams:
        """Transform query."""
        return ECBEuroShortTermRateQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: ECBEuroShortTermRateQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Fetch the €STR data types."""
        # pylint: disable=import-outside-toplevel
        from openbb_ecb.utils.data_cache import cached_records, make_key
        from openbb_ecb.utils.query_builder import fetch_sdmx_data
        from openbb_ecb.utils.series_keys import est_key

        start = query.start_date.strftime("%Y-%m-%d") if query.start_date else None
        end = query.end_date.strftime("%Y-%m-%d") if query.end_date else None

        async def loader() -> list[dict]:
            return await fetch_sdmx_data(
                "EST", est_key(), start_date=start, end_date=end, raise_empty=False
            )

        cache_key = make_key("estr", start=start, end=end)
        records = await cached_records(
            "estr", cache_key, loader, use_cache=query.use_cache
        )
        if not records:
            raise OpenBBError(EmptyDataError("No €STR data found for the query."))
        return records

    @staticmethod
    def transform_data(
        query: ECBEuroShortTermRateQueryParams, data: list[dict], **kwargs: Any
    ) -> list[ECBEuroShortTermRateData]:
        """Pivot the data-type series into one record per date."""
        # pylint: disable=import-outside-toplevel
        from openbb_ecb.utils.series_keys import EST_DATA_TYPES

        by_date: dict[str, dict] = {}
        for record in data:
            data_type = record.get("DATA_TYPE_EST")
            field = (
                EST_DATA_TYPES.get(data_type) if isinstance(data_type, str) else None
            )
            value = record.get("OBS_VALUE")
            if field is None or value is None:
                continue
            row = by_date.setdefault(record["date"], {"date": record["date"]})
            if field in _PERCENT_FIELDS:
                row[field] = float(value) / 100
            elif field in _INT_FIELDS:
                row[field] = int(value)
            else:
                row[field] = float(value)

        results = [
            ECBEuroShortTermRateData.model_validate(row)
            for row in by_date.values()
            if row.get("rate") is not None
        ]
        results.sort(key=lambda r: r.date)
        return results
